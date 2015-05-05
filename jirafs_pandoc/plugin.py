import datetime
import os
import shutil
import subprocess
import tempfile

import six

from jirafs.plugin import Plugin, PluginOperationError, PluginValidationError


class Pandoc(Plugin):
    """ Converts various markups into other document formats for JIRA.

    By default, jirafs_pandoc will convert all known markdown,
    reStructuredText, and textile documents into fancy PDFs during the
    upload process.

    See documentation at http://github.com/coddingtonbear/jirafs-pandoc
    for more details.

    """
    MIN_VERSION = '0.9.0'
    MAX_VERSION = '1.99.99'

    SUPPORTED_INPUT_FORMATS = {
        "extra": ["text", "txt"],
        "html": ["html", "htm"],
        "json": ["json"],
        "latex": ["latex", "tex", "ltx"],
        "markdown": ["markdown", "mkd", "md", "pandoc", "pdk", "pd", "pdc"],
        "native": ["hs"],
        "rst": ["rst"],
        "textile": ["textile"]
    }
    DEFAULT_FORMATS = ['markdown', 'rst', 'textile']

    def get_format_from_path(self, path):
        extension = os.path.splitext(path)[1][1:]
        for format_name, extensions in self.SUPPORTED_INPUT_FORMATS.items():
            if extension in extensions:
                return format_name
        raise PluginOperationError(
            "Unable to find format matching extension %s" % extension
        )

    def get_output_format(self, actual=False):
        config = self.get_configuration()
        value = config.get('output_format', 'pdf').lower()
        if actual and value == 'pdf':
            return 'latex'
        return value

    def get_enabled_input_extensions(self):
        config = self.get_configuration()

        formats = config.get('enabled_input_formats', None)
        extensions = config.get('enabled_input_extensions', None)

        if not formats:
            formats = self.DEFAULT_FORMATS
        else:
            formats = formats.split(',')

        enabled = []
        if not formats and not extensions:
            for supported in self.SUPPORTED_INPUT_FORMATS.values():
                for v in supported:
                    enabled.append(v)
        else:
            if formats:
                for format_name in formats:
                    for v in self.SUPPORTED_INPUT_FORMATS[format_name]:
                        enabled.append(v)
            if extensions:
                enabled.extend(extensions.split(','))

        return enabled

    def get_username_and_email(self):
        try:
            name = subprocess.check_output([
                'git',
                'config',
                'user.name',
            ]).decode('utf8').strip()
            email = subprocess.check_output([
                'git',
                'config',
                'user.email',
            ]).decode('utf8').strip()
            return '%s <%s>' % (
                name,
                email,
            )
        except (subprocess.CalledProcessError, OSError, IOError):
            return ''

    def get_command_args(self, original_filename, file_path):
        command = [
            'pandoc',
            '--from=%s' % self.get_format_from_path(original_filename),
            '--to=%s' % self.get_output_format(actual=True),
            '-o',
            file_path
        ]
        if self.get_output_format() == 'pdf':
            template_path = os.path.join(
                os.path.dirname(__file__),
                'pdf_template.tex',
            )
            version = "Updated %s UTC" % (
                datetime.datetime.utcnow().isoformat()[0:16]
            )
            command.extend([
                '--template=%s' % template_path,
                '--variable', 'version=%s' % version,
                '--variable', 'author=%s' % self.get_username_and_email(),
                '--latex-engine=xelatex',
            ])

        return command

    def alter_file_upload(self, info):
        metadata = self.get_metadata()

        filename, file_object = info

        basename, extension = os.path.splitext(filename)
        if extension[1:] not in self.get_enabled_input_extensions():
            return filename, file_object
        new_filename = '.'.join([basename, self.get_output_format()])

        tempdir = tempfile.mkdtemp()
        temp_file_path = os.path.join(
            tempdir,
            new_filename,
        )

        proc = subprocess.Popen(
            self.get_command_args(filename, temp_file_path),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(file_object.read())

        if proc.returncode:
            raise PluginOperationError(
                "%s encountered an error while compiling from %s to %s: %s" % (
                    self.plugin_name,
                    extension,
                    self.get_output_format(),
                    stderr,
                )
            )

        with open(temp_file_path, 'rb') as temp_output:
            content = six.BytesIO(temp_output.read())
        shutil.rmtree(tempdir)

        filename_map = metadata.get('filename_map', {})
        filename_map[new_filename] = filename
        metadata['filename_map'] = filename_map
        self.set_metadata(metadata)

        return new_filename, content

    def validate(self):
        requirements = {
            'pandoc': ['pandoc', '-v']
        }
        if self.get_output_format() == 'pdf':
            requirements['latex'] = ['xelatex', '-v']

        for req_name, args in requirements.items():
            try:
                subprocess.check_call(
                    args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except (subprocess.CalledProcessError, IOError, OSError):
                raise PluginValidationError(
                    "%s requires %s to be installed." % (
                        self.plugin_name,
                        req_name,
                    )
                )

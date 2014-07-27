import datetime
import os
import shutil
import subprocess
import tempfile

import six

from jirafs.plugin import Plugin, PluginOperationError, PluginValidationError


class Pandoc(Plugin):
    MIN_VERSION = '0.9.0'
    MAX_VERSION = '0.99.99'

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

    def get_format_from_path(self, path):
        extension = os.path.splitext(path)[1:]
        for format_name, extension_list in self.SUPPORTED_INPUT_FORMATS:
            if extension in extension_list:
                return format_name
        raise PluginOperationError(
            "Unable to find format matching extension %s" % extension
        )

    def get_output_format(self):
        config = self.get_configuration()
        return config.get('output_format', 'pdf').lower()

    def get_enabled_input_extensions(self):
        config = self.get_configuration()

        formats = config.get('enabled_input_formats', None)
        extensions = config.get('enabled_input_extensions', None)

        enabled = []
        if not formats and not extensions:
            for supported in self.SUPPORTED_INPUT_VALUES.values():
                for v in supported:
                    enabled.append(v)
        else:
            if formats:
                for format_name in formats.split(','):
                    for v in self.SUPPORTED_INPUT_FORMATS[format_name]:
                        enabled.append(v)
            if extensions:
                enabled.extend(extensions)

        return enabled

    def get_command_args(self, file_path):
        command = [
            'pandoc',
            '--from=%s' % self.get_format_from_path(file_path),
            '--to=%s' % self.get_output_format(),
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
            self.get_command_args(temp_file_path),
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
                    self.OUTPUT_EXTENSION,
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

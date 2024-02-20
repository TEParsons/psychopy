
from setuptools import Command
from babel.messages import frontend as babel

class CompileMo(Command):
    description = "Compile PO files to MO files"

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for locale, po_file in self.distribution.metadata.get_translations():
            mo_file = po_file.replace(".po", ".mo")
            babel.compile_catalog(locale, po_file, mo_file)

if __name__ == "__main__":
    import setuptools
    setuptools.setup(
        # ... other setup options
        cmdclass={"compile_mo": CompileMo},
    )
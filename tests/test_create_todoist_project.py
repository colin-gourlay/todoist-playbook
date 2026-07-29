import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / ".github" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import create_todoist_project


class CreateTodoistProjectDescriptionTests(unittest.TestCase):
    def test_explicit_project_description_takes_priority(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            template_dir = Path(tmpdir)
            (template_dir / "meta.yml").write_text(
                "name: Demo Template\ndescription: Template description\n",
                encoding="utf-8",
            )

            description = create_todoist_project.resolve_project_description(
                str(template_dir), "Workflow override"
            )

            self.assertEqual(description, "Workflow override")

    def test_template_meta_description_is_used_when_not_overridden(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            template_dir = Path(tmpdir)
            (template_dir / "meta.yml").write_text(
                "name: Demo Template\ndescription: Template description\n",
                encoding="utf-8",
            )

            description = create_todoist_project.resolve_project_description(
                str(template_dir), ""
            )

            self.assertEqual(description, "Template description")


if __name__ == "__main__":
    unittest.main()

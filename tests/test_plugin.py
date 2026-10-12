"""Plugin packaging/local project installation regressions; no accounts or network."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from package_plugin import NAME, SKILLS, build_zip, path_inside, records, validate_plugin, verify_zip, write_directory
from install_plugin import prepare, install


class PluginTests(unittest.TestCase):
    def test_manifest_components_and_no_mcp(self):
        self.assertEqual(validate_plugin()['name'],NAME)
        self.assertEqual(json.loads((ROOT/'mcp.json').read_text(encoding='utf-8'))['mcpServers'],{})
        self.assertEqual(set(p.name for p in (ROOT/'skills').iterdir() if p.is_dir()),set(SKILLS))

    def test_zip_reproducible_and_complete(self):
        with tempfile.TemporaryDirectory(prefix='plugin сборка ') as directory:
            a,b=Path(directory)/'a.zip',Path(directory)/'b.zip'
            build_zip(a);build_zip(b)
            self.assertEqual(a.read_bytes(),b.read_bytes())
            self.assertEqual(verify_zip(a)['skills'],13)
            with zipfile.ZipFile(a) as archive:
                self.assertIn(NAME+'/skills/ig-human/ru_lexicon.json',archive.namelist())
                self.assertIn(NAME+'/skills/ig-plan/references/onboarding.md',archive.namelist())
                license=(ROOT/'LICENSE').read_bytes().replace(b'\r\n',b'\n')
                for name in SKILLS:
                    self.assertEqual(archive.read(f'{NAME}/skills/{name}/LICENSE'),license)

    def test_zip_rejects_traversal_and_runtime_files(self):
        with tempfile.TemporaryDirectory() as directory:
            for suffix in ('../escape.txt','.test-work/auth.json'):
                p=Path(directory)/'bad.zip'
                with zipfile.ZipFile(p,'w') as archive:archive.writestr(NAME+'/'+suffix,'bad')
                with self.assertRaises(ValueError):verify_zip(p)

    def test_zip_hash_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'bad.zip';data=records();data['plugin.json']=b'{}'
            with zipfile.ZipFile(p,'w') as archive:
                for rel,raw in data.items():archive.writestr(NAME+'/'+rel,raw)
            with self.assertRaises(ValueError):verify_zip(p)

    def test_clean_package_snapshot_and_conflict(self):
        with tempfile.TemporaryDirectory() as directory:
            dest=Path(directory)/'plugin'
            write_directory(dest)
            self.assertEqual(validate_plugin(dest)['name'],NAME)
            self.assertEqual(write_directory(dest),dest)
            (dest/'plugin.json').write_text('{}',encoding='utf-8')
            with self.assertRaises(ValueError):write_directory(dest)

    def test_no_private_or_unreviewed_package_files(self):
        data=records()
        for rel in data:
            self.assertFalse(any(x in rel for x in ('auth.json','.test-work','__pycache__','.git/','outputs/')))
        self.assertEqual(len([rel for rel in data if rel.endswith('/SKILL.md')]),13)

    def test_path_rules(self):
        for rel in ('../outside','/absolute','./../outside',r'.\skills'):
            with self.subTest(rel=rel):
                with self.assertRaises(ValueError):path_inside(ROOT,rel)

    def test_profile_preflight_no_writes(self):
        with tempfile.TemporaryDirectory(prefix='plugin профиль ') as directory:
            profile=Path(directory)/'profile';package=Path(directory)/'package'
            result=install(profile,package,True)
            self.assertTrue(result['dry_run'])
            self.assertFalse(profile.exists())
            self.assertFalse(package.exists())

    def test_profile_source_conflict_before_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            profile=Path(directory)/'profile';package=Path(directory)/'package'
            package.mkdir();(package/'plugin.json').write_text('{}',encoding='utf-8')
            with self.assertRaises(ValueError):install(profile,package,True)
            self.assertFalse(profile.exists())

    def test_profile_overlap_and_global_home_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):prepare(Path(directory)/'source/profile',Path(directory)/'source')
        with self.assertRaises(ValueError):install(Path.home(),dry_run=True)
        with self.assertRaises(ValueError):install(Path.home()/'.codex',dry_run=True)


if __name__=='__main__':unittest.main()

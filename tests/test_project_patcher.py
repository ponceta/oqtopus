"""Tests for oqtopus.utils.project_patcher."""

import zipfile

from oqtopus.utils.project_patcher import (
    patch_project_file,
    patch_qgs_file,
    patch_qgz_file,
    replace_service_in_content,
)

# ---------------------------------------------------------------------------
# replace_service_in_content
# ---------------------------------------------------------------------------


class TestReplaceServiceInContent:
    def test_single_quoted(self):
        xml = "dbname='' service='pg_old' sslmode=disable"
        result = replace_service_in_content(xml, "pg_new")
        assert result == "dbname='' service='pg_new' sslmode=disable"

    def test_xml_apos(self):
        xml = "service=&apos;pg_old&apos; key=&apos;other&apos;"
        result = replace_service_in_content(xml, "pg_new")
        assert "service=&apos;pg_new&apos;" in result
        # Non-service apos values are untouched
        assert "key=&apos;other&apos;" in result

    def test_xml_quot(self):
        xml = "service=&quot;pg_old&quot;"
        result = replace_service_in_content(xml, "pg_new")
        assert result == "service=&quot;pg_new&quot;"

    def test_multiple_occurrences(self):
        xml = (
            "<datasource>service='pg_old' table=x</datasource>\n"
            "<datasource>service='pg_old' table=y</datasource>"
        )
        result = replace_service_in_content(xml, "pg_new")
        assert result.count("service='pg_new'") == 2
        assert "pg_old" not in result

    def test_no_match_unchanged(self):
        xml = "<tag>no service here</tag>"
        result = replace_service_in_content(xml, "pg_new")
        assert result == xml


# ---------------------------------------------------------------------------
# patch_qgs_file
# ---------------------------------------------------------------------------


class TestPatchQgsFile:
    def test_patches_file(self, tmp_path):
        src = tmp_path / "project.qgs"
        src.write_text(
            "<qgis><datasource>service='orig_svc' table=t</datasource></qgis>",
            encoding="utf-8",
        )
        dst = tmp_path / "output.qgs"
        patch_qgs_file(str(src), str(dst), "new_svc")
        contents = dst.read_text(encoding="utf-8")
        assert "service='new_svc'" in contents
        assert "orig_svc" not in contents

    def test_in_place(self, tmp_path):
        src = tmp_path / "project.qgs"
        src.write_text("service='old'", encoding="utf-8")
        patch_qgs_file(str(src), str(src), "new")
        assert "service='new'" in src.read_text()


# ---------------------------------------------------------------------------
# patch_qgz_file
# ---------------------------------------------------------------------------


def _make_qgz(qgz_path, qgs_content, extra_files=None):
    """Helper: create a .qgz containing a .qgs and optional extra files."""
    with zipfile.ZipFile(qgz_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("project.qgs", qgs_content)
        for name, content in (extra_files or {}).items():
            zf.writestr(name, content)


class TestPatchQgzFile:
    def test_patches_inner_qgs(self, tmp_path):
        src = tmp_path / "project.qgz"
        _make_qgz(
            str(src),
            "<qgis><datasource>service='pg_orig'</datasource></qgis>",
        )
        dst = tmp_path / "patched.qgz"
        patch_qgz_file(str(src), str(dst), "pg_target")

        # Verify the inner .qgs was patched
        with zipfile.ZipFile(str(dst), "r") as zf:
            inner = zf.read("project.qgs").decode("utf-8")
        assert "service='pg_target'" in inner
        assert "pg_orig" not in inner

    def test_preserves_extra_files(self, tmp_path):
        src = tmp_path / "project.qgz"
        _make_qgz(
            str(src),
            "service='old'",
            extra_files={"style.qml": "<qgis_style/>", "data/readme.txt": "hello"},
        )
        dst = tmp_path / "patched.qgz"
        patch_qgz_file(str(src), str(dst), "new")

        with zipfile.ZipFile(str(dst), "r") as zf:
            names = set(zf.namelist())
            assert "style.qml" in names
            assert zf.read("style.qml") == b"<qgis_style/>"
            assert zf.read("data/readme.txt") == b"hello"

    def test_in_place(self, tmp_path):
        src = tmp_path / "project.qgz"
        _make_qgz(str(src), "service='old'")
        patch_qgz_file(str(src), str(src), "new")

        with zipfile.ZipFile(str(src), "r") as zf:
            inner = zf.read("project.qgs").decode("utf-8")
        assert "service='new'" in inner


# ---------------------------------------------------------------------------
# patch_project_file  (high-level dispatcher)
# ---------------------------------------------------------------------------


class TestPatchProjectFile:
    def test_qgs(self, tmp_path):
        src = tmp_path / "p.qgs"
        src.write_text("service='a'", encoding="utf-8")
        dst = tmp_path / "out.qgs"
        patch_project_file(str(src), str(dst), "b")
        assert "service='b'" in dst.read_text()

    def test_qgz(self, tmp_path):
        src = tmp_path / "p.qgz"
        _make_qgz(str(src), "service='a'")
        dst = tmp_path / "out.qgz"
        patch_project_file(str(src), str(dst), "b")
        with zipfile.ZipFile(str(dst), "r") as zf:
            assert "service='b'" in zf.read("project.qgs").decode()

    def test_none_service_copies_without_patching(self, tmp_path):
        src = tmp_path / "p.qgs"
        src.write_text("service='keep_me'", encoding="utf-8")
        dst = tmp_path / "out.qgs"
        patch_project_file(str(src), str(dst), None)
        assert "service='keep_me'" in dst.read_text()

    def test_none_service_noop_when_same_path(self, tmp_path):
        src = tmp_path / "p.qgs"
        src.write_text("service='keep_me'", encoding="utf-8")
        patch_project_file(str(src), str(src), None)
        assert "service='keep_me'" in src.read_text()

    def test_unknown_extension_copies(self, tmp_path):
        src = tmp_path / "p.txt"
        src.write_text("service='x'", encoding="utf-8")
        dst = tmp_path / "out.txt"
        patch_project_file(str(src), str(dst), "y")
        # Unknown format → plain copy, no patching
        assert "service='x'" in dst.read_text()

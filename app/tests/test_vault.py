import pytest

from app.services.vault import list_existing_folders, list_notes, read_note


def test_list_existing_folders_finds_nested_dirs_and_skips_hidden(tmp_path):
    (tmp_path / "astronomia" / "galaxias").mkdir(parents=True)
    (tmp_path / "electricidad").mkdir()
    (tmp_path / ".git").mkdir()
    (tmp_path / "README.md").write_text("hola")

    result = list_existing_folders(str(tmp_path))

    assert set(result) == {"astronomia", "astronomia/galaxias", "electricidad"}


def test_list_notes_finds_nested_md_files(tmp_path):
    (tmp_path / "astronomia" / "galaxias").mkdir(parents=True)
    (tmp_path / "astronomia" / "galaxias" / "via-lactea.md").write_text("contenido")
    (tmp_path / "electricidad").mkdir()
    (tmp_path / "electricidad" / "tipos-de-corriente.md").write_text("contenido")
    (tmp_path / "README.md").write_text("contenido")

    result = list_notes(str(tmp_path))

    assert {(note.path, note.folder) for note in result} == {
        ("astronomia/galaxias/via-lactea.md", "astronomia/galaxias"),
        ("electricidad/tipos-de-corriente.md", "electricidad"),
        ("README.md", ""),
    }


def test_list_notes_skips_non_markdown_and_hidden_dirs(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config.md").write_text("no debería contar")
    (tmp_path / "notas.txt").write_text("no es markdown")
    (tmp_path / "real.md").write_text("contenido")

    result = list_notes(str(tmp_path))

    assert [note.path for note in result] == ["real.md"]


def test_list_notes_returns_empty_list_for_empty_vault(tmp_path):
    assert list_notes(str(tmp_path)) == []


def test_read_note_returns_content_for_existing_file(tmp_path):
    (tmp_path / "electricidad").mkdir()
    (tmp_path / "electricidad" / "tipos-de-corriente.md").write_text("# Contenido real")

    result = read_note(str(tmp_path), "electricidad/tipos-de-corriente.md")

    assert result.path == "electricidad/tipos-de-corriente.md"
    assert result.folder == "electricidad"
    assert result.content == "# Contenido real"


def test_read_note_returns_none_for_missing_file(tmp_path):
    assert read_note(str(tmp_path), "no-existe.md") is None


def test_read_note_returns_none_for_non_markdown_file(tmp_path):
    (tmp_path / "notas.txt").write_text("no es markdown")

    assert read_note(str(tmp_path), "notas.txt") is None


def test_read_note_returns_none_for_hidden_path_segment(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config.md").write_text("no debería contar")

    assert read_note(str(tmp_path), ".git/config.md") is None


def test_read_note_raises_value_error_for_path_traversal(tmp_path):
    with pytest.raises(ValueError):
        read_note(str(tmp_path), "../fuera-del-vault.md")

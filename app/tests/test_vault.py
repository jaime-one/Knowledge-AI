from app.services.vault import list_existing_folders, list_notes


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

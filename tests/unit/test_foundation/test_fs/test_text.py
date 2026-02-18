"""foundation.fs.text モジュールのテスト

ファイル読み取り・書き込み専用クラスをテストします。
"""

import os
from pathlib import Path

import pytest

from example.foundation.fs import (
    FileSystemError,
    TextFileSystemReader,
    TextFileSystemWriter,
)


class TestTextFileSystemReader:
    """TextFileSystemReader クラスのテスト"""

    def test_read_正常系_ファイル内容を文字列で返す(self, tmp_path: Path):
        # Arrange
        test_file = tmp_path / "test_reader.txt"
        content = """line1
line2
日本語テスト"""
        test_file.write_text(content, encoding="utf-8")

        reader = TextFileSystemReader()

        # Act
        result = reader.read(test_file)

        # Assert
        expected = "line1\nline2\n日本語テスト"
        assert result == expected

    def test_read_正常系_空ファイルで空文字列返却(self, tmp_path: Path):
        # Arrange
        test_file = tmp_path / "empty.txt"
        test_file.write_text("", encoding="utf-8")

        reader = TextFileSystemReader()

        # Act
        result = reader.read(test_file)

        # Assert
        assert result == ""

    def test_read_異常系_存在しないファイルでFileSystemError(self):
        # Arrange
        reader = TextFileSystemReader()

        # Act & Assert
        with pytest.raises(FileSystemError):
            reader.read(Path("存在しないファイル.txt"))

    @pytest.mark.skipif(os.name == "nt", reason="Unix系システムでのみ有効な権限テスト")
    def test_read_異常系_権限なしファイルでFileSystemError(self, tmp_path: Path):
        # Arrange
        test_file = tmp_path / "no_permission.txt"
        test_file.write_text("test content", encoding="utf-8")

        # ファイルの読み取り権限を削除（Unixシステムでのみ有効）
        test_file.chmod(0o000)

        reader = TextFileSystemReader()

        # Act & Assert
        try:
            with pytest.raises(FileSystemError):
                reader.read(test_file)
        finally:
            # テスト後に権限を復元（クリーンアップのため）
            test_file.chmod(0o644)

    def test_read_異常系_エンコーディング不正でFileSystemError(self, tmp_path: Path):
        # Arrange
        test_file = tmp_path / "invalid_encoding.txt"

        # latin-1エンコーディングでUTF-8で読めない文字を書き込み
        with test_file.open("w", encoding="latin-1") as f:
            f.write("àáâãäåæçèéêë\xff\xfe")  # latin-1固有文字

        reader = TextFileSystemReader()

        # Act & Assert
        with pytest.raises(FileSystemError):
            reader.read(test_file)  # UTF-8で読み込もうとして失敗


class TestTextFileSystemWriter:
    """TextFileSystemWriter クラスのテスト"""

    def test_write_正常系_新規ファイルに書き込み成功する(self, tmp_path: Path):
        # Arrange
        test_file = tmp_path / "test_write.txt"
        content = "Hello\nWorld\n日本語コンテンツ"

        writer = TextFileSystemWriter()

        # Act
        writer.write(content, test_file)

        # Assert
        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == content

    def test_write_正常系_既存ファイル上書き成功する(self, tmp_path: Path):
        # Arrange
        test_file = tmp_path / "test_overwrite.txt"
        original_content = "original content"
        new_content = "new content\n新しい内容"

        # 既存ファイル作成
        test_file.write_text(original_content, encoding="utf-8")

        writer = TextFileSystemWriter()

        # Act
        writer.write(new_content, test_file)

        # Assert
        assert test_file.read_text(encoding="utf-8") == new_content

    def test_write_正常系_空文字列書き込み成功する(self, tmp_path: Path):
        # Arrange
        test_file = tmp_path / "empty_write.txt"
        content = ""

        writer = TextFileSystemWriter()

        # Act
        writer.write(content, test_file)

        # Assert
        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == ""

    def test_write_正常系_UTF8文字エンコーディング処理(self, tmp_path: Path):
        # Arrange
        test_file = tmp_path / "utf8_write.txt"
        content = "特殊文字テスト: éñ中文한글🎉"

        writer = TextFileSystemWriter()

        # Act
        writer.write(content, test_file)

        # Assert
        assert test_file.read_text(encoding="utf-8") == content

    def test_write_正常系_存在しないディレクトリを自動作成する(self, tmp_path: Path):
        # Arrange
        nested_dir = tmp_path / "level1" / "level2" / "level3"
        test_file = nested_dir / "test.txt"
        content = "auto mkdir test"

        # ディレクトリが存在しないことを確認
        assert not nested_dir.exists()

        writer = TextFileSystemWriter()

        # Act
        writer.write(content, test_file)

        # Assert
        # ディレクトリが自動作成され、ファイルが正常に保存されることを確認
        assert nested_dir.exists()
        assert nested_dir.is_dir()
        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == content

    def test_write_異常系_ファイルパスがディレクトリでFileSystemError(self, tmp_path: Path):
        # Arrange
        test_dir = tmp_path / "test_directory"
        test_dir.mkdir()

        writer = TextFileSystemWriter()

        # Act & Assert
        with pytest.raises(FileSystemError) as exc_info:
            writer.write("test content", test_dir)

        error = exc_info.value
        assert "指定されたパスはディレクトリです" in error.message
        assert str(test_dir) in error.message

    @pytest.mark.skipif(os.name == "nt", reason="Unix系システムでのみ有効な権限テスト")
    def test_write_異常系_権限なしディレクトリでFileSystemError(self, tmp_path: Path):
        # Arrange
        test_dir = tmp_path / "no_write_permission"
        test_dir.mkdir()
        test_file = test_dir / "test.txt"

        # ディレクトリの書き込み権限を削除(Unixシステムでのみ有効)
        test_dir.chmod(0o555)

        writer = TextFileSystemWriter()

        # Act & Assert
        try:
            with pytest.raises(FileSystemError) as exc_info:
                writer.write("test content", test_file)

            error = exc_info.value
            assert "ファイルへの書き込み権限がありません" in error.message
            assert str(test_file) in error.message
        finally:
            # テスト後に権限を復元(クリーンアップのため)
            test_dir.chmod(0o755)

    def test_write_正常系_戻り値なし確認(self, tmp_path: Path):
        # Arrange
        test_file = tmp_path / "return_test.txt"
        content = "return value test"

        writer = TextFileSystemWriter()

        # Act
        result = writer.write(content, test_file)

        # Assert
        assert result is None

    def test_write_異常系_ファイル名不正でFileSystemError(self, tmp_path: Path):
        # Arrange
        # NULL文字を含む不正なファイル名
        invalid_filename = "test\x00file.txt"
        test_file = tmp_path / invalid_filename

        writer = TextFileSystemWriter()

        # Act & Assert
        with pytest.raises(FileSystemError) as exc_info:
            writer.write("test content", test_file)

        error = exc_info.value
        assert "ファイル書き込み中にエラーが発生しました" in error.message

    @pytest.mark.skipif(os.name == "nt", reason="Unix系システムでのみ有効な権限テスト")
    def test_write_異常系_ディレクトリ作成権限なしでFileSystemError(self, tmp_path: Path):
        # Arrange
        test_dir = tmp_path / "no_mkdir_permission"
        test_dir.mkdir()

        # ディレクトリの書き込み権限を削除(サブディレクトリ作成不可)
        test_dir.chmod(0o555)

        test_file = test_dir / "newdir" / "test.txt"

        writer = TextFileSystemWriter()

        # Act & Assert
        try:
            with pytest.raises(FileSystemError) as exc_info:
                writer.write("test content", test_file)

            error = exc_info.value
            assert "ディレクトリの作成権限がありません" in error.message
            assert str(test_dir / "newdir") in error.message
        finally:
            # テスト後に権限を復元(クリーンアップのため)
            test_dir.chmod(0o755)

    def test_write_異常系_ディレクトリ作成時の予期しないエラーでFileSystemError(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        # Arrange
        test_file = tmp_path / "test" / "test.txt"
        target_dir = test_file.parent

        # Path.mkdirをモックして、予期しないエラーを発生させる
        original_mkdir = Path.mkdir

        def mock_mkdir(
            self: Path,
            mode: int = 0o777,
            parents: bool = False,
            exist_ok: bool = False,
        ) -> None:
            if self == target_dir:
                raise OSError("予期しないファイルシステムエラー")
            return original_mkdir(self, mode, parents, exist_ok)

        monkeypatch.setattr(Path, "mkdir", mock_mkdir)

        writer = TextFileSystemWriter()

        # Act & Assert
        with pytest.raises(FileSystemError) as exc_info:
            writer.write("test content", test_file)

        error = exc_info.value
        assert "ディレクトリの作成に失敗しました" in error.message

    def test_単一責任_書き込み機能のみ提供(self):
        # Arrange
        writer = TextFileSystemWriter()

        # Act & Assert
        # 書き込み機能のみ存在することを確認
        assert hasattr(writer, "write")

        # 読み取り・バリデーション機能は存在しないことを確認
        assert not hasattr(writer, "read")
        assert not hasattr(writer, "check_file")
        assert not hasattr(writer, "check_directory")

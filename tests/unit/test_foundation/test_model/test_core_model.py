"""CoreModelの基盤機能テスト

pydanticの基本機能とプロジェクト固有の設定をテストします。
"""

import pytest
from pydantic import Field, ValidationError

from example.foundation.model import CoreModel


class SampleCoreModel(CoreModel):
    """テスト用のCoreModelサブクラス"""

    name: str
    value: int
    description: str = Field(alias="desc")


@pytest.fixture
def sample_core_model_data() -> dict[str, str | int]:
    """SampleCoreModel用の基本テストデータ"""
    return {"name": "test", "value": 42, "desc": "test description"}


@pytest.fixture
def sample_core_model(sample_core_model_data: dict[str, str | int]) -> SampleCoreModel:
    """SampleCoreModelのテスト用インスタンス"""
    return SampleCoreModel.model_validate(sample_core_model_data)


class TestCoreModelBasicFunctionality:
    """CoreModelの基本機能テスト"""

    def test_create_正常系_基本的なオブジェクト作成(self, sample_core_model: SampleCoreModel):
        assert sample_core_model.name == "test"
        assert sample_core_model.value == 42
        assert sample_core_model.description == "test description"

    def test_frozen_正常系_不変オブジェクトである(self, sample_core_model: SampleCoreModel):
        with pytest.raises(ValidationError):
            sample_core_model.name = "modified"

        with pytest.raises(ValidationError):
            sample_core_model.value = 100


class TestCoreModelValidation:
    """CoreModelのバリデーション機能テスト"""

    def test_model_validate_正常系_dictから正常にオブジェクトを作成(self):
        data: dict[str, str | int] = {
            "name": "test_model",
            "value": 123,
            "description": "test description",
        }

        test_obj = SampleCoreModel.model_validate(data)

        assert test_obj.name == "test_model"
        assert test_obj.value == 123
        assert test_obj.description == "test description"

    def test_model_validate_異常系_必須フィールド不足でValidationError(self):
        incomplete_data: dict[str, str] = {
            "name": "test",
            # valueフィールドが不足
            "description": "test desc",
        }

        with pytest.raises(ValidationError) as exc_info:
            SampleCoreModel.model_validate(incomplete_data)

        error = exc_info.value
        assert error.error_count() == 1
        errors = error.errors()
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("value",)
        assert "value" in str(error)

    def test_model_validate_異常系_不正な型でValidationError(self):
        invalid_data: dict[str, str] = {
            "name": "test",
            "value": "not_integer",  # 本来はint
            "description": "test desc",
        }

        with pytest.raises(ValidationError) as exc_info:
            SampleCoreModel.model_validate(invalid_data)

        error = exc_info.value
        assert error.error_count() == 1
        errors = error.errors()
        assert errors[0]["type"] == "int_parsing"
        assert errors[0]["loc"] == ("value",)
        assert "value" in str(error)


class TestCoreModelExtraFields:
    """CoreModelのextra="forbid"機能テスト"""

    def test_extra_forbid_異常系_未知フィールドでValidationError(self):
        data_with_unknown: dict[str, str | int] = {
            "name": "test",
            "value": 42,
            "description": "test desc",
            "unknown_field": "should_not_be_allowed",  # 未知フィールド
        }

        with pytest.raises(ValidationError) as exc_info:
            SampleCoreModel.model_validate(data_with_unknown)

        error = exc_info.value
        assert error.error_count() == 1
        errors = error.errors()
        assert errors[0]["type"] == "extra_forbidden"
        assert errors[0]["loc"] == ("unknown_field",)
        assert "unknown_field" in str(error)

    def test_extra_forbid_正常系_既知フィールドのみは正常動作(self):
        valid_data: dict[str, str | int] = {"name": "test", "value": 42, "description": "test desc"}

        test_obj = SampleCoreModel.model_validate(valid_data)
        assert test_obj.name == "test"


class TestCoreModelWhitespaceStripping:
    """CoreModelのstr_strip_whitespace=True機能テスト"""

    @pytest.mark.parametrize(
        "input_name,expected_name,input_description,expected_description",
        [
            ("  test_name  ", "test_name", "\t test description \n", "test description"),
            ("   ", "", "valid desc", "valid desc"),
            ("\n\tname\t\n", "name", "  desc  ", "desc"),
        ],
    )
    def test_str_strip_whitespace_正常系_文字列前後の空白を自動除去(
        self, input_name: str, expected_name: str, input_description: str, expected_description: str
    ):
        data: dict[str, str | int] = {
            "name": input_name,
            "value": 42,
            "description": input_description,
        }

        test_obj = SampleCoreModel.model_validate(data)

        assert test_obj.name == expected_name
        assert test_obj.description == expected_description


class TestCoreModelAliasSupport:
    """CoreModelのpopulate_by_name=True機能テスト"""

    def test_populate_by_name_正常系_エイリアス名で入力可能(self):
        data_with_alias: dict[str, str | int] = {
            "name": "test",
            "value": 42,
            "desc": "test using alias",  # "description"のエイリアス
        }

        test_obj = SampleCoreModel.model_validate(data_with_alias)

        assert test_obj.description == "test using alias"

    def test_populate_by_name_正常系_フィールド名でも入力可能(self):
        data_with_field_name: dict[str, str | int] = {
            "name": "test",
            "value": 42,
            "description": "test using field name",  # 実際のフィールド名
        }

        test_obj = SampleCoreModel.model_validate(data_with_field_name)

        assert test_obj.description == "test using field name"

    def test_populate_by_name_異常系_エイリアスとフィールド名両方指定でValidationError(self):
        data_with_both: dict[str, str | int] = {
            "name": "test",
            "value": 42,
            "desc": "via alias",
            "description": "via field name",  # 同時指定は不可
        }

        with pytest.raises(ValidationError) as exc_info:
            SampleCoreModel.model_validate(data_with_both)

        error = exc_info.value
        assert error.error_count() >= 1
        errors = error.errors()
        # エイリアスとフィールド名の競合エラー
        assert any("desc" in str(err["loc"]) or "description" in str(err["loc"]) for err in errors)
        assert "desc" in str(error) or "description" in str(error)


class TestCoreModelCopyFunctionality:
    """CoreModelのmodel_copy()機能テスト"""

    def test_model_copy_正常系_基本的なコピー機能(self, sample_core_model: SampleCoreModel):
        copied = sample_core_model.model_copy()

        assert copied.name == sample_core_model.name
        assert copied.value == sample_core_model.value
        assert copied.description == sample_core_model.description
        assert copied is not sample_core_model  # 別オブジェクト

    def test_model_copy_正常系_update引数で一部フィールドを更新(
        self, sample_core_model: SampleCoreModel
    ):
        updated = sample_core_model.model_copy(update={"name": "updated", "value": 200})

        assert updated.name == "updated"
        assert updated.value == 200
        assert updated.description == sample_core_model.description  # 更新されていない

        # 元のオブジェクトは変更されない
        assert sample_core_model.name == "test"
        assert sample_core_model.value == 42

    def test_model_copy_正常系_deep_copy機能(self, sample_core_model: SampleCoreModel):
        deep_copied = sample_core_model.model_copy(deep=True)

        assert deep_copied.name == sample_core_model.name
        assert deep_copied.value == sample_core_model.value
        assert deep_copied is not sample_core_model

    def test_model_copy_正常系_不変性により元オブジェクト保護(
        self, sample_core_model: SampleCoreModel
    ):
        # コピー作成
        copied = sample_core_model.model_copy(update={"name": "modified"})

        # 元オブジェクトは不変
        assert sample_core_model.name == "test"
        assert copied.name == "modified"

        # 元オブジェクトの直接変更は依然として不可
        with pytest.raises(ValidationError):
            sample_core_model.name = "should_fail"

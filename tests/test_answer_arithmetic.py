"""Specific carrying/regrouping explanations for the primary worked keys."""
import ast

from tools.improve_primary_arithmetic import addition, numbers_for_addition, subtraction


def test_multi_addend_working_includes_both_carries():
    steps = addition([567, 23, 126])
    assert "7 + 3 + 6 = 16" in steps[0] and "Write 6" in steps[0] and "Carry 1" in steps[0]
    assert "6 + 2 + 2 + 1 = 11" in steps[1] and "Write 1" in steps[1]
    assert "5 + 0 + 1 + 1 = 7" in steps[2]
    assert steps[-1].endswith("716.")


def test_regrouping_across_zero_columns_is_explained_correctly():
    steps = subtraction(1000, 1)
    assert "make 10" in steps[0]
    assert "10 - 1 = 9" in steps[1]
    assert any("Tens column: 9 - 0 = 9" in step for step in steps)
    assert any("Hundreds column: 9 - 0 = 9" in step for step in steps)
    assert steps[-1] == "Read the result: 999. Check: 999 + 1 = 1000."


def test_subtraction_repeated_regrouping_has_correct_intermediate_digits():
    steps = subtraction(1111, 888)
    assert any("11 - 8 = 3" in step for step in steps)
    assert sum("10 - 8 = 2" in step for step in steps) == 2
    assert "223 + 888 = 1111" in steps[-1]


def test_swahili_working_uses_place_value_terms():
    steps = addition([99, 1], sw=True)
    assert "Safu ya moja: 9 + 1 = 10" in steps[0]
    assert "Peleka 1" in steps[0]
    assert "Safu ya makumi: 9 + 0 + 1 = 10" in steps[1]
    assert steps[-1].endswith("100.")


def test_complex_or_negative_expressions_are_not_rewritten_as_column_addition():
    assert numbers_for_addition(ast.parse("(5 + 3) * 2", mode="eval").body) is None
    assert numbers_for_addition(ast.parse("-3 + 9", mode="eval").body) is None

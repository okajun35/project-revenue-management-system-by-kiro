from typing import List, Tuple
from app.models import Branch


def build_branch_choices(include_placeholder: bool = False) -> List[Tuple[int, str]]:
    """支社のSelectField用choicesを返す。

    include_placeholder: 先頭にプレースホルダを含める場合はTrue
    """
    choices = [(branch.id, branch.branch_name) for branch in Branch.get_active_branches()]
    if include_placeholder:
        choices = [(0, '支社を選択してください')] + choices
    return choices


def build_fiscal_year_choices(include_placeholder: bool = False) -> List[Tuple[int, str]]:
    """年度のSelectField用choicesを返す。

    include_placeholder: 先頭にプレースホルダを含める場合はTrue
    """
    from app.models import FiscalYear
    choices = [(year.year, year.year_name) for year in FiscalYear.get_active_years()]
    if include_placeholder:
        choices = [(0, '年度を選択してください')] + choices
    return choices

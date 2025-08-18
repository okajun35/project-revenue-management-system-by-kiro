"""
ダッシュボード統計情報サービス

統計情報の計算とダッシュボード関連のビジネスロジックを提供します。
"""

from sqlalchemy import func, desc
from sqlalchemy.exc import OperationalError
from app import db
from app.models import Project, Branch


class DashboardService:
    """ダッシュボード統計情報サービス"""
    
    @staticmethod
    def get_overall_stats(fiscal_year=None):
        """
        全体統計情報を取得
        
        Args:
            fiscal_year (int, optional): 特定年度の統計を取得する場合に指定
            
        Returns:
            dict: 統計情報
        """
        try:
            query = Project.query
            if fiscal_year:
                query = query.filter(Project.fiscal_year == fiscal_year)
            # 基本統計
            total_projects = query.count()
            # 売上・経費・粗利の合計
            totals = db.session.query(
                func.sum(Project.revenue).label('total_revenue'),
                func.sum(Project.expenses).label('total_expenses')
            )
            if fiscal_year:
                totals = totals.filter(Project.fiscal_year == fiscal_year)
            result = totals.first()
            total_revenue = float(result.total_revenue or 0)
            total_expenses = float(result.total_expenses or 0)
            total_gross_profit = total_revenue - total_expenses
        except OperationalError:
            # 初回起動などDB未初期化時のフォールバック
            total_projects = 0
            total_revenue = 0.0
            total_expenses = 0.0
            total_gross_profit = 0.0
        return {
            'total_projects': total_projects,
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'total_gross_profit': total_gross_profit,
            'fiscal_year': fiscal_year
        }
    
    @staticmethod
    def get_yearly_trend_data():
        """
        年度別売上推移データを取得
        
        Returns:
            dict: 年度別データ（年度、売上、経費、粗利）
        """
        try:
            yearly_data = db.session.query(
                Project.fiscal_year,
                func.sum(Project.revenue).label('total_revenue'),
                func.sum(Project.expenses).label('total_expenses'),
                func.count(Project.id).label('project_count')
            ).group_by(Project.fiscal_year).order_by(Project.fiscal_year).all()
        except OperationalError:
            yearly_data = []
        
        years = []
        revenues = []
        expenses = []
        profits = []
        project_counts = []
        
        for data in yearly_data:
            years.append(data.fiscal_year)
            revenue = float(data.total_revenue or 0)
            expense = float(data.total_expenses or 0)
            revenues.append(revenue)
            expenses.append(expense)
            profits.append(revenue - expense)
            project_counts.append(data.project_count)
        
        return {
            'years': years,
            'revenues': revenues,
            'expenses': expenses,
            'profits': profits,
            'project_counts': project_counts
        }
    
    @staticmethod
    def get_branch_stats(fiscal_year=None):
        """
        支社別統計情報を取得
        
        Args:
            fiscal_year (int, optional): 特定年度の統計を取得する場合に指定
            
        Returns:
            list: 支社別統計情報のリスト
        """
        try:
            if fiscal_year:
                # 特定年度の場合：年度フィルターを適用したプロジェクトとの LEFT JOIN
                query = db.session.query(
                    Branch.id,
                    Branch.branch_code,
                    Branch.branch_name,
                    func.count(Project.id).label('project_count'),
                    func.sum(Project.revenue).label('total_revenue'),
                    func.sum(Project.expenses).label('total_expenses')
                ).outerjoin(
                    Project,
                    db.and_(
                        Branch.id == Project.branch_id,
                        Project.fiscal_year == fiscal_year
                    )
                )
            else:
                # 全年度の場合：通常の LEFT JOIN
                query = db.session.query(
                    Branch.id,
                    Branch.branch_code,
                    Branch.branch_name,
                    func.count(Project.id).label('project_count'),
                    func.sum(Project.revenue).label('total_revenue'),
                    func.sum(Project.expenses).label('total_expenses')
                ).outerjoin(Project, Branch.id == Project.branch_id)
            query = query.filter(Branch.is_active == True).group_by(
                Branch.id, Branch.branch_code, Branch.branch_name
            ).order_by(Branch.branch_name)
            branch_stats = []
            for data in query.all():
                revenue = float(data.total_revenue or 0)
                expenses = float(data.total_expenses or 0)
                gross_profit = revenue - expenses
                branch_stats.append({
                    'branch_id': data.id,
                    'branch_code': data.branch_code,
                    'branch_name': data.branch_name,
                    'project_count': data.project_count,
                    'total_revenue': revenue,
                    'total_expenses': expenses,
                    'total_gross_profit': gross_profit,
                    'gross_profit_rate': (gross_profit / revenue * 100) if revenue > 0 else 0
                })
        except OperationalError:
            branch_stats = []
        
        return branch_stats
    
    @staticmethod
    def get_recent_projects(limit=5):
        """
        最近更新されたプロジェクト一覧を取得
        
        Args:
            limit (int): 取得件数（デフォルト: 5件）
            
        Returns:
            list: プロジェクトのリスト
        """
        try:
            projects = Project.query.join(Branch).order_by(
                desc(Project.updated_at)
            ).limit(limit).all()
            return [project.to_dict() for project in projects]
        except OperationalError:
            return []
    
    @staticmethod
    def get_available_years():
        """
        利用可能な年度一覧を取得
        
        Returns:
            list: 年度のリスト（降順）
        """
        try:
            years = db.session.query(Project.fiscal_year).distinct().order_by(
                desc(Project.fiscal_year)
            ).all()
        except OperationalError:
            years = []
        return [year[0] for year in years] if years else []
    
    @staticmethod
    def get_top_projects_by_revenue(fiscal_year=None, limit=10):
        """
        売上上位プロジェクトを取得
        
        Args:
            fiscal_year (int, optional): 特定年度のプロジェクトを取得する場合に指定
            limit (int): 取得件数（デフォルト: 10件）
            
        Returns:
            list: プロジェクトのリスト
        """
        query = Project.query.join(Branch)
        
        if fiscal_year:
            query = query.filter(Project.fiscal_year == fiscal_year)
        
        projects = query.order_by(desc(Project.revenue)).limit(limit).all()
        
        return [project.to_dict() for project in projects]
    
    @staticmethod
    def get_order_probability_distribution(fiscal_year=None):
        """
        受注角度別分布を取得
        
        Args:
            fiscal_year (int, optional): 特定年度の分布を取得する場合に指定
            
        Returns:
            dict: 受注角度別の件数と売上
        """
        query = db.session.query(
            Project.order_probability,
            func.count(Project.id).label('count'),
            func.sum(Project.revenue).label('total_revenue')
        )
        
        if fiscal_year:
            query = query.filter(Project.fiscal_year == fiscal_year)
        
        query = query.group_by(Project.order_probability).order_by(Project.order_probability)
        
        distribution = {}
        for data in query.all():
            prob_value = int(data.order_probability)
            if prob_value == 100:
                label = '〇（確実）'
            elif prob_value == 50:
                label = '△（可能性あり）'
            else:
                label = '×（困難）'
            
            distribution[label] = {
                'count': data.count,
                'total_revenue': float(data.total_revenue or 0),
                'probability_value': prob_value
            }
        
        return distribution
    
    @staticmethod
    def get_monthly_revenue_trend(fiscal_year, branch_ids=None, order_probabilities=None):
        """
        月別売上推移データを取得
        
        Args:
            fiscal_year (int): 対象年度
            branch_ids (list, optional): 対象支社IDのリスト
            order_probabilities (list, optional): 対象受注角度のリスト（0, 50, 100）
            
        Returns:
            dict: 月別売上データ
        """
        from datetime import datetime, date
        from calendar import monthrange
        
        # 年度の開始・終了月を計算
        if fiscal_year:
            start_date = date(fiscal_year, 4, 1)  # 4月1日開始
            end_date = date(fiscal_year + 1, 3, 31)  # 翌年3月31日終了
        else:
            # 現在の年度を推定
            today = date.today()
            if today.month >= 4:
                fiscal_year = today.year
                start_date = date(fiscal_year, 4, 1)
                end_date = date(fiscal_year + 1, 3, 31)
            else:
                fiscal_year = today.year - 1
                start_date = date(fiscal_year, 4, 1)
                end_date = date(fiscal_year + 1, 3, 31)
        
        # 基本クエリ
        query = db.session.query(
            Project.id,
            Project.project_code,
            Project.project_name,
            Project.revenue,
            Project.expenses,
            Project.order_probability,
            Project.branch_id,
            Branch.branch_name,
            Branch.branch_code,
            Project.created_at
        ).join(Branch, Project.branch_id == Branch.id)
        
        # 年度フィルタ
        query = query.filter(Project.fiscal_year == fiscal_year)
        
        # 支社フィルタ
        if branch_ids:
            query = query.filter(Project.branch_id.in_(branch_ids))
        
        # 受注角度フィルタ
        if order_probabilities:
            query = query.filter(Project.order_probability.in_(order_probabilities))
        
        projects = query.all()
        
        # 月別データを初期化（4月から3月まで）
        months = []
        month_labels = []
        
        current_date = start_date
        while current_date <= end_date:
            months.append(current_date.month)
            month_labels.append(f"{current_date.year}/{current_date.month:02d}")
            
            # 次の月へ
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)
        
        # 全体データ
        overall_data = {month: {'revenue': 0, 'expenses': 0, 'count': 0} for month in month_labels}
        
        # 支社別データ
        branch_data = {}
        
        # プロジェクトデータを月別に集計
        for project in projects:
            # プロジェクトの作成月を取得（年度内の月に分散）
            created_at = project.created_at
            
            # 年度内の月に均等分散（簡易的な実装）
            if created_at.month >= 4:
                fiscal_month = created_at.month
                fiscal_year_for_month = created_at.year
            else:
                fiscal_month = created_at.month
                fiscal_year_for_month = created_at.year
            
            project_month = f"{fiscal_year_for_month}/{fiscal_month:02d}"
            
            if project_month in overall_data:
                # 全体データに追加
                overall_data[project_month]['revenue'] += float(project.revenue or 0)
                overall_data[project_month]['expenses'] += float(project.expenses or 0)
                overall_data[project_month]['count'] += 1
                
                # 支社別データに追加
                branch_key = f"{project.branch_code}_{project.branch_name}"
                if branch_key not in branch_data:
                    branch_data[branch_key] = {
                        'branch_id': project.branch_id,
                        'branch_code': project.branch_code,
                        'branch_name': project.branch_name,
                        'data': {month: {'revenue': 0, 'expenses': 0, 'count': 0} for month in month_labels}
                    }
                
                branch_data[branch_key]['data'][project_month]['revenue'] += float(project.revenue or 0)
                branch_data[branch_key]['data'][project_month]['expenses'] += float(project.expenses or 0)
                branch_data[branch_key]['data'][project_month]['count'] += 1
        
        # データを整形
        result = {
            'fiscal_year': fiscal_year,
            'months': month_labels,
            'overall': {
                'revenues': [overall_data[month]['revenue'] for month in month_labels],
                'expenses': [overall_data[month]['expenses'] for month in month_labels],
                'profits': [overall_data[month]['revenue'] - overall_data[month]['expenses'] for month in month_labels],
                'counts': [overall_data[month]['count'] for month in month_labels]
            },
            'branches': []
        }
        
        # 支社別データを追加
        for branch_key, branch_info in branch_data.items():
            branch_result = {
                'branch_id': branch_info['branch_id'],
                'branch_code': branch_info['branch_code'],
                'branch_name': branch_info['branch_name'],
                'revenues': [branch_info['data'][month]['revenue'] for month in month_labels],
                'expenses': [branch_info['data'][month]['expenses'] for month in month_labels],
                'profits': [branch_info['data'][month]['revenue'] - branch_info['data'][month]['expenses'] for month in month_labels],
                'counts': [branch_info['data'][month]['count'] for month in month_labels]
            }
            result['branches'].append(branch_result)
        
        return result
    
    @staticmethod
    def get_available_branches():
        """
        利用可能な支社一覧を取得
        
        Returns:
            list: 支社のリスト
        """
        branches = Branch.query.filter(Branch.is_active == True).order_by(Branch.branch_name).all()
        
        return [{
            'id': branch.id,
            'code': branch.branch_code,
            'name': branch.branch_name
        } for branch in branches]
    
    @staticmethod
    def get_available_order_probabilities():
        """
        利用可能な受注角度一覧を取得
        
        Returns:
            list: 受注角度のリスト
        """
        return [
            {'value': 100, 'label': '〇（確実）', 'symbol': '〇'},
            {'value': 50, 'label': '△（可能性あり）', 'symbol': '△'},
            {'value': 0, 'label': '×（困難）', 'symbol': '×'}
        ]
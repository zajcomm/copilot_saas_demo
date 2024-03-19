from django.views.generic import TemplateView
from django.conf import settings
from . import api


FILE_PATH = 'conduit/files/orders.csv'

# File columns is a definition for a CSV file, so Copilot could correctly parse it.
# Each column definition constists of:
#   name: name of a column, must be same as in CSV file
#   kind: one of DIMENSION | METRIC
#   type:
#       for kind=DIMENSION only STRING | DATE | DATETIME | BOOL values are allowed
#       for kind=METRIC only MONEY | DECIMAL | INTEGER | PERCENT values are allowed
#   agg:
#       for kind=DIMENSION only UNIQ value is allowed
#       for kind=METRIC only SUM | COUNT | AVERAGE | MAX | MIN | FIRST values are allowed
#  is_enabled: if false, than copilot will not use this field
#  description: optional field, which can be used for passing information about field to the Copilot
FILE_COLUMNS = [
    api.SpreadsheetColumn(
        name='Date',
        kind=api.ColumnKindEnum.DIMENSION,
        type=api.ColumnTypeEnum.STRING,
        agg=api.AggregationTypeEnum.UNIQ,
        is_enabled=True,
        description='Date when order was created',
    ),
    api.SpreadsheetColumn(
        name='Order ID',
        kind=api.ColumnKindEnum.DIMENSION,
        type=api.ColumnTypeEnum.STRING,
        agg=api.AggregationTypeEnum.UNIQ,
        is_enabled=True,
        description='ID on an order',
    ),
    api.SpreadsheetColumn(
        name='Customer Email',
        kind=api.ColumnKindEnum.DIMENSION,
        type=api.ColumnTypeEnum.STRING,
        agg=api.AggregationTypeEnum.UNIQ,
        is_enabled=True,
        description='',
    ),
    api.SpreadsheetColumn(
        name='Price',
        kind=api.ColumnKindEnum.METRIC,
        type=api.ColumnTypeEnum.DECIMAL,
        agg=api.AggregationTypeEnum.SUM,
        is_enabled=True,
        description='Price in USD dollars',
    ),
]

USER_ID = '1'


class IndexView(TemplateView):
    template_name = 'index.html'

    def post(self, request, *args, **kwargs):
        action = request.POST['action']

        match action:
            case 'upload':
                spreadsheet_id = self._do_upload()
                return super().get(request, show_upload=False, show_new_chat=True, spreadsheet_id=spreadsheet_id)
            case 'new_chat':
                chat_url = self._do_create_chat(request.POST['spreadsheet_id'])
                return super().get(request, show_upload=False, show_chat=True, chat_url=chat_url)

        return super().get(request)

    def get_context_data(self, **kwargs):
        return {
            'show_upload': True,
            'show_new_chat': False,
            'show_chat': False,
            **kwargs,
        }

    def _do_upload(self):
        # check if company exists

        link_api = api.LinkAppAPI(token=settings.LINK_TOKEN)
        company_token = link_api.get_company_token(USER_ID)

        copilot = api.CopilotAPI(token=company_token)
        uploaded_file = copilot.upload_file(settings.BASE_DIR / FILE_PATH)
        spreadsheet = copilot.create_spreadsheet(
            file_id=uploaded_file.file_id,
            name='Orders',
            columns=FILE_COLUMNS,
        )

        return spreadsheet.id

    def _do_create_chat(self, spreadsheet_id):
        link_api = api.LinkAppAPI(token=settings.LINK_TOKEN)
        company_token = link_api.get_company_token(USER_ID)

        copilot = api.CopilotAPI(token=company_token)

        chat = copilot.create_chat('Orders', spreadsheet_id)

        return chat.url

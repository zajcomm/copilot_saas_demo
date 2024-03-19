import datetime
from enum import Enum
from typing import Any, BinaryIO, Literal
from urllib.parse import urljoin
from pathlib import Path

import requests
from pydantic import BaseModel


SeparatorT = Literal['.', ',']


class CompanyLinkPage(BaseModel):
    url: str | None
    enabled: bool


class CompanyApiToken(BaseModel):
    token: str
    expires_at: int


class Company(BaseModel):
    id: str
    name: str
    created_at: datetime.datetime
    link_page: CompanyLinkPage | None
    api_token: CompanyApiToken


class UploadedFile(BaseModel):
    file_id: int


class ColumnKindEnum(str, Enum):
    DIMENSION = 'DIMENSION'
    METRIC = 'METRIC'


class ColumnTypeEnum(str, Enum):
    # Dimensions
    STRING = 'STRING'
    DATE = 'DATE'
    DATETIME = 'DATETIME'
    BOOL = 'BOOL'
    # Metrics
    MONEY = 'MONEY'
    DECIMAL = 'DECIMAL'
    INTEGER = 'INTEGER'
    PERCENT = 'PERCENT'


class AggregationTypeEnum(str, Enum):
    # Dimensions
    UNIQ = 'UNIQ'
    # Metrics
    SUM = 'SUM'
    COUNT = 'COUNT'
    AVERAGE = 'AVERAGE'
    MAX = 'MAX'
    MIN = 'MIN'
    FIRST = 'FIRST'


class SpreadsheetColumn(BaseModel):
    is_enabled: bool
    name: str
    kind: ColumnKindEnum
    type: ColumnTypeEnum
    agg: AggregationTypeEnum
    description: str = ''


class Spreadsheet(BaseModel):
    name: str
    thousands_separator: SeparatorT
    decimal_separator: SeparatorT
    read_from_line: int
    columns: list[SpreadsheetColumn]


class SpreadsheetID(BaseModel):
    id: int


class Chat(BaseModel):
    id: int
    name: str
    url: str


class _API:
    API_URL = 'https://api.getconduit.app/'

    def __init__(self, token: str) -> None:
        self._token = token

    def _request(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | None = None,
        files: dict[str, BinaryIO] | None = None,
    ) -> requests.Response:

        res = requests.request(
            method=method,
            url=urljoin(self.API_URL, path),
            json=data,
            files=files,
            headers={
                'Authorization': f'Bearer {self._token}',
            },
        )
        res.raise_for_status()

        return res


class LinkAppAPI(_API):

    def create_company(self, company_id: str, name: str | None = None) -> Company:
        res = self._request(
            'POST',
            '/link/company/',
            data={'id': company_id, 'name': name or f'Company #{company_id}'},
        )

        return Company.model_validate_json(res.content)

    def get_company(self, company_id: str) -> Company:
        res = self._request('GET', f'/link/company/{company_id}/')

        return Company.model_validate_json(res.content)

    def get_company_token(self, company_id: str) -> str:
        try:
            company = self.get_company(company_id)
        except requests.HTTPError as ex:
            if ex.response.status_code == 404:
                company = self.create_company(company_id)
            else:
                raise

        return company.api_token.token


class CopilotAPI(_API):

    def upload_file(self, file_path: str | Path) -> UploadedFile:
        res = self._request(
            'POST',
            '/copilot_saas/spreadsheets/upload/',
            files={
                'file': open(file_path, 'rb'),
            },
        )

        return UploadedFile.model_validate_json(res.content)

    def create_spreadsheet(
        self,
        file_id: int,
        name: str,
        columns: list[SpreadsheetColumn],
        thousands_separator: SeparatorT = '.',
        decimal_separator: SeparatorT = ',',
        read_from_line: int = 1,
    ) -> SpreadsheetID:

        res = self._request(
            'POST',
            '/copilot_saas/spreadsheets/',
            data={
                'file_id': file_id,
                'name': name,
                'thousands_separator': thousands_separator,
                'decimal_separator': decimal_separator,
                'read_from_line': read_from_line,
                'columns': [col.model_dump() for col in columns],
            },
        )

        return SpreadsheetID.model_validate_json(res.content)

    def create_chat(self, name: str, spreadsheet_id: int) -> Chat:
        res = self._request(
            'POST',
            '/copilot_saas/chats/',
            data={
                'name': name,
                'datasets': [
                    {'type': 'SPREADSHEET', 'id': spreadsheet_id},
                ],
            },
        )

        return Chat.model_validate_json(res.content)

import json

from aiexec.custom import Component
from aiexec.inputs import BoolInput, StrInput
from aiexec.schema import Data
from aiexec.template import Output


class TextToData(Component):
    inputs = [
        StrInput(name="text_data", is_list=True),
        BoolInput(name="is_json", info="Parse text_data as json and fill the data object."),
    ]
    outputs = [
        Output(name="from_text", display_name="From text", method="create_data"),
    ]

    def _to_data(self, text: str) -> Data:
        if self.is_json:
            return Data(data=json.loads(text))
        return Data(text=text)

    def create_data(self) -> list[Data]:
        return [self._to_data(t) for t in self.text_data]

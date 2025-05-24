class Text(str):
    @classmethod
    def from_markup(cls, text: str) -> "Text":
        return cls(text)

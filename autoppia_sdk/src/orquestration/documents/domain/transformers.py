from typing import List

from bs4 import BeautifulSoup
from langchain.text_splitter import (
    CharacterTextSplitter as LangchainCharacterTextSplitter,
)
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
from langchain.text_splitter import TokenTextSplitter as LangchainTokenTextSplitter
from pydantic import BaseModel

from autoppia_agentic_framework.src.chains.domain.classes import Chain
from autoppia_agentic_framework.src.documents.domain.classes import Document, DocumentList
from autoppia_agentic_framework.src.llms.domain.interfaces.models import ILLMModel


class DocumentTransformer(BaseModel):
    def serialize_documents(self, documents: List[Document]) -> str:
        serialized_docs = [str(doc) for doc in documents]
        return f"[{', '.join(serialized_docs)}]"


class TextSplitter(DocumentTransformer):
    separator: str = "\n\n"
    chunkSize: int = 10000

    def transform(self, documents: List[Document]) -> List[Document]:
        return DocumentList.fromLangchainDocuments(self.splitByTokenLength(documents))

    def splitByCharacter(self, raw_documents: List[str]) -> List[str]:
        text_splitter = LangchainCharacterTextSplitter(
            separator=self.separator, chunk_size=self.chunkSize, chunk_overlap=0
        )
        return text_splitter.split_documents(raw_documents)

    def splitByTokenLength(self, raw_documents: List[str]) -> List[str]:
        text_splitter = LangchainCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=self.chunkSize, chunk_overlap=0, separator=self.separator
        )
        return text_splitter.split_documents(raw_documents)


class TokenTextSplitter(DocumentTransformer):
    chunkSize: int = 10000

    def transform(self, documents: List[Document]) -> List[Document]:
        newDocuments = []
        for document in documents:
            for newDocument in DocumentList.fromStringList(
                self.split(document.page_content), metadata=document.metadata
            ):
                newDocuments.append(newDocument)
        return newDocuments

    def split(self, text: str) -> List[str]:
        return LangchainTokenTextSplitter(
            chunk_size=self.chunkSize, disallowed_special=()
        ).split_text(str(text))


class ProgrammingLanguageSplitter(DocumentTransformer):
    chunkSize: int = 12000
    language: Language = Language.HTML

    def transform(self, documents: List[Document]) -> List[Document]:
        return DocumentList.fromLangchainDocuments(self.splitByCharacter(documents))

    def splitByCharacter(self, raw_documents: List[str]) -> List[str]:
        text_splitter = RecursiveCharacterTextSplitter.from_language(
            self.language, chunk_size=self.chunkSize
        )
        return text_splitter.split_documents(raw_documents)


class ContextualCompressor(DocumentTransformer):
    compressionRules: List[str]
    minimumTokenLength: int = 15000

    def __init__(self, llmModel: ILLMModel):
        self.llmModel: ILLMModel = llmModel

    def transform(self, documents: List[Document]) -> List[Document]:
        newDocuments = []
        for document in documents:
            compressionChain = Chain(
                self.model,
                Chain.getinstructionsTemplate("transformer/contextualCompressor"),
                useCache=False,
                cacheName="tool_needed",
            )
            compressedText = compressionChain.run(
                document.page_content,
                variablesToReplace={"compressionRules": self.compressionRules},
            )
            newDocuments.append(Document(compressedText, document.metadata))
        return newDocuments


class HTMLBeautifulSoupTransformer(DocumentTransformer):
    def transform(self, documents: List[Document]) -> List[Document]:
        for document in documents:
            soup = BeautifulSoup(str(document.page_content), "html.parser")
            document.metadata["type"] = "BeautifulSoup"
            document.page_content = str(
                HTMLBeautifulSoupTransformer.extract_important_info(soup)
            )
        return documents

    @staticmethod
    def extract_import_info_from_html(html: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        return HTMLBeautifulSoupTransformer.extract_important_info(soup)

    @staticmethod
    def extract_important_info(soup: BeautifulSoup) -> dict:
        soup = HTMLBeautifulSoupTransformer.cleanSoup(soup)

        important_elements = {}

        # Find and save buttons
        important_elements["buttons"] = [button for button in soup.find_all("button")]

        # Find and save form input fields
        important_elements["inputs"] = [
            input_tag for input_tag in soup.find_all("input")
        ]

        # Find and save dropdown lists
        important_elements["selects"] = [select for select in soup.find_all("select")]

        # Find and save text areas
        important_elements["textareas"] = [
            textarea for textarea in soup.find_all("textarea")
        ]

        # Find and save hyperlinks
        important_elements["links"] = [link for link in soup.find_all("a")]

        # # Find and save images
        # important_elements['images'] = [img for img in soup.find_all('img')]

        # # Find and save divs with ids or classes
        # important_elements['divs'] = [div for div in soup.find_all('div', {'id': True})] + \
        #                             [div for div in soup.find_all('div', {'class': True})]

        # Find and save forms
        important_elements["forms"] = [form for form in soup.find_all("form")]

        # Find and save radio buttons and checkboxes
        important_elements["radios_checkboxes"] = [
            input_tag
            for input_tag in soup.find_all("input", {"type": ["radio", "checkbox"]})
        ]

        # Find and save labels
        important_elements["labels"] = [label for label in soup.find_all("label")]

        # Find and save headings
        important_elements["headings"] = [
            heading for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        ]

        # Find and save tables
        important_elements["tables"] = [table for table in soup.find_all("table")]

        # # Find and save lists
        # important_elements['lists'] = [list_tag for list_tag in soup.find_all(['ul', 'ol'])]

        # # Find and save meta tags
        # important_elements['meta'] = [meta for meta in soup.find_all('meta')]

        return important_elements

    def extract_simplified_info(html: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        simplified_info = {}

        # Define your abbreviations
        abbreviations = {
            "nth-of-type": "nth",
            # Add other abbreviations as needed
        }

        # Extract navbar
        navbars = soup.find_all("nav")
        navbars += [
            element
            for element in soup.find_all(True)
            if "navbar" in (element.get("class") or [])
        ]

        simplified_info["navbars"] = [
            {
                "id": navbar.get("id"),
                "name": navbar.get("name"),
                "selector": f"{navbar.name}:nth-of-type({index})"
                if not navbar.get("id") and not navbar.get("name")
                else None,
            }
            for index, navbar in enumerate(navbars, start=1)
        ]

        simplified_info["links"] = [
            {
                "href": link.get("href"),
                "id": link.get("id"),
                "name": link.get("name"),
                "selector": f"a:nth-of-type({index})"
                if not link.get("id") and not link.get("name")
                else None,
            }
            for index, link in enumerate(soup.find_all("a"), start=1)
        ]

        simplified_info["forms"] = [
            {
                "action": form.get("action"),
                "id": form.get("id"),
                "name": form.get("name"),
                "selector": f"form:nth-of-type({index})"
                if not form.get("id") and not form.get("name")
                else None,
            }
            for index, form in enumerate(soup.find_all("form"), start=1)
        ]

        simplified_info["buttons"] = [
            {
                "text": button.text.strip(),
                "id": button.get("id"),
                "name": button.get("name"),
                "selector": f"button:nth-of-type({index})"
                if not button.get("id") and not button.get("name")
                else None,
            }
            for index, button in enumerate(soup.find_all("button"), start=1)
            if button.text.strip()
        ]

        simplified_info["inputs"] = [
            {
                "type": input_tag.get("type"),
                "id": input_tag.get("id"),
                "name": input_tag.get("name"),
                "selector": f"input:nth-of-type({index})"
                if not input_tag.get("id") and not input_tag.get("name")
                else None,
            }
            for index, input_tag in enumerate(soup.find_all("input"), start=1)
        ]

        simplified_info["selects"] = [
            {
                "id": select.get("id"),
                "name": select.get("name"),
                "selector": f"select:nth-of-type({index})"
                if not select.get("id") and not select.get("name")
                else None,
            }
            for index, select in enumerate(soup.find_all("select"), start=1)
        ]

        simplified_info["headings"] = [
            {
                "text": heading.text.strip(),
                "id": heading.get("id"),
                "name": heading.get("name"),
                "selector": f"{heading.name}:nth-of-type({index})"
                if not heading.get("id") and not heading.get("name")
                else None,
            }
            for index, heading in enumerate(
                soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]), start=1
            )
            if heading.text.strip()
        ]

        # function
        def clean_dict(d):
            # Remove keys with value None
            cleaned = {k: v for k, v in d.items() if v is not None}

            # If the cleaned dictionary only contains the key 'selector', return None
            if len(cleaned) == 1 and "selector" in cleaned:
                return None

            return cleaned

        # Clean the dictionaries in the resulting dictionary
        for key in list(simplified_info.keys()):
            if isinstance(simplified_info[key], list):
                # Clean dictionaries and remove those that are None after cleaning
                simplified_info[key] = [
                    item
                    for item in (clean_dict(d) for d in simplified_info[key])
                    if item is not None
                ]

                # If after cleaning, the list is empty, remove the key from simplified_info
                if not simplified_info[key]:
                    del simplified_info[key]

            elif isinstance(simplified_info[key], dict):
                simplified_info[key] = clean_dict(simplified_info[key])

                # If after cleaning, the dictionary is empty or None, remove the key from simplified_info
                if not simplified_info[key]:
                    del simplified_info[key]

        # Function
        def abbreviate_strings(input_dict, abbreviations):
            def recursive_abbreviate(item):
                if isinstance(item, dict):
                    return {k: recursive_abbreviate(v) for k, v in item.items()}
                elif isinstance(item, list):
                    return [recursive_abbreviate(elem) for elem in item]
                elif isinstance(item, str):
                    for long_string, abbreviation in abbreviations.items():
                        item = item.replace(long_string, abbreviation)
                    return item
                else:
                    return (
                        item  # Return the item as is if it's not a dict, list, or str
                    )

            return recursive_abbreviate(input_dict)

            return recursive_abbreviate(input_dict)

        # Abbreviate strings in the dictionary before returning it
        elements = abbreviate_strings(simplified_info, abbreviations)
        elements["abreviations"] = abbreviations
        return elements

    @staticmethod
    def cleanSoup(soup: BeautifulSoup) -> BeautifulSoup:
        for tag in soup.find_all(True):
            if "class" in tag.attrs:
                del tag.attrs["class"]
            if "style" in tag.attrs:
                del tag.attrs["style"]

        return soup

from dataclasses import dataclass
import json
from typing import Any


@dataclass
class ModuleConferencePart():
    module_id: int
    hide_cover_slide: bool

@dataclass 
class CoverSlideConferencePartImage():
    base64: str

@dataclass
class CoverSlideConferencePart():
    title: str
    image: CoverSlideConferencePartImage | None


@dataclass
class Conference:
    title: str
    subtitle: str
    parts: list[ModuleConferencePart | CoverSlideConferencePart]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(title=data.get('title'), subtitle=data.get('subtitle'), parts=[
            (ModuleConferencePart(module_id=session_part.get('module_id'), hide_cover_slide=session_part.get('hide_cover_slide')) 
                if session_part.get('module_id') 
                else CoverSlideConferencePart(title=session_part.get('title'), image=(
                    CoverSlideConferencePartImage(base64=session_part.get('image').get('base64')) 
                    if session_part.get('image') is not None 
                    else None
                )))
            for session_part in data.get('parts')])

    @classmethod
    def get_default(cls):
        return  cls(title='Ma conférence', subtitle='Accroche', parts=[])


def serialize_conference(conference: Conference) -> str:
    def serialize_part(p: ModuleConferencePart | CoverSlideConferencePart) -> dict :
        if isinstance(p, ModuleConferencePart):
            return { "kind": "module", "module_id": p.module_id, "hide_cover_slide": p.hide_cover_slide }
        elif isinstance(p, CoverSlideConferencePart):
            return { "kind": "cover_slide", "title": p.title, "image_base64": p.image.base64 if p.image is not None else None }
        else:
            raise ValueError('Unable to serialize part')
        

    to_export = {
        "parts": list(map(serialize_part, conference.parts)),
        "title": conference.title,
        "subtitle": conference.subtitle,
        "version": 2
    }
    return json.dumps(to_export, indent=4)

def deserialize_conference(serialized: str) -> Conference:
    parsed = json.loads(serialized)
    if (parsed["version"] == 1):
        return parse_conference_v1(parsed)
    elif (parsed["version"] == 2):
        return parse_conference_v2(parsed)
    else:
        raise NotImplementedError(f'Parser not implemented for version: {parsed["version"]}')

def parse_conference_v1(conference: Any) -> Conference:
    return Conference(
        parts=list(map(lambda m_id: ModuleConferencePart(module_id=m_id, hide_cover_slide=False), conference["modules"])), 
        title=conference["title"] if "title" in conference else "", 
        subtitle=conference["subtitle"] if "subtitle" in conference else ""
    )

def parse_conference_v2(conference: Any) -> Conference:
    def deserialize_part(p: Any) -> ModuleConferencePart | CoverSlideConferencePart :
        if p["kind"] == "module":
            return ModuleConferencePart(module_id=p["module_id"], hide_cover_slide=p["hide_cover_slide"])
        elif p["kind"] == "cover_slide":
            return CoverSlideConferencePart(title=p["title"], image=(CoverSlideConferencePartImage(base64=p["image_base64"]) if ("image_base64" in p and p["image_base64"] is not None) else None))
        else:
            raise ValueError('Unable to deserialize part')
    return Conference(
        parts=list(map(deserialize_part, conference["parts"])), 
        title=conference["title"], 
        subtitle=conference["subtitle"]
    )
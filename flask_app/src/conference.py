from dataclasses import dataclass
import json
from typing import Any


@dataclass
class ModuleConferencePart():
    module_id: int

@dataclass
class CoverSlideConferencePart():
    title: str

@dataclass
class Conference:
    title: str
    subtitle: str
    parts: list[ModuleConferencePart | CoverSlideConferencePart]

def serialize_conference(conference: Conference) -> str:
    def serialize_part(p: ModuleConferencePart | CoverSlideConferencePart) -> dict :
        if isinstance(p, ModuleConferencePart):
            return { "kind": "module", "module_id": p.module_id }
        elif isinstance(p, CoverSlideConferencePart):
            return { "kind": "cover_slide", "title": p.title }
        else:
            raise ValueError('Unable to serialize part')
        

    to_export = {
        "parts": list(map(serialize_part, conference.parts)),
        "title": conference.title,
        "subtitle": conference.subtitle,
        "version": 2
    }
    return json.dumps(to_export)

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
        parts=list(map(lambda m_id: ModuleConferencePart(module_id=m_id), conference["modules"])), 
        title=conference["title"] if "title" in conference else "", 
        subtitle=conference["subtitle"] if "subtitle" in conference else ""
    )

def parse_conference_v2(conference: Any) -> Conference:
    raise NotImplementedError('unimplemented')
from . import routes
from flask import render_template
from modules import conference_modules_service
from itertools import groupby

@routes.route('/module/<int:module_id>')
def module_details(module_id: int):
    module = conference_modules_service.get_module_by_id(module_id)
    return render_template('details.html', 
                            module_id = module.id,
                            image_url = module.img_url,
                            title = module.title,
                            description = module.description,
                            duration_minutes = module.duration_minutes,
                            maintainer = module.maintainer,
                            sources = module.sources,
                            changes = module.changes,
                            messages = module.messages,
                            tags_categories = [ { "category": k, "tags": [tag.tag for tag in v] } for k, v in groupby(module.tags, lambda t:t.category) ],
                            is_valid = module.is_valid,
                            invalid_reason = module.invalid_reason)
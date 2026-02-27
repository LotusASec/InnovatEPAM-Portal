# Import models so SQLAlchemy metadata is populated before create_all()
from app.models.user import User  # noqa: F401
from app.models.idea import Idea  # noqa: F401
from app.models.attachment import Attachment  # noqa: F401
from app.models.evaluation_comment import EvaluationComment  # noqa: F401

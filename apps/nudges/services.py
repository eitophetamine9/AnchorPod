from django.contrib.auth import get_user_model
from apps.pods.models import PodMembership
from .models import NudgeTemplate, Nudge

User = get_user_model()

DEFAULT_TEMPLATES = [
    {
        "message": "Thinking of you today! Take it one step at a time.",
        "category": "gentle",
    },
    {
        "message": "Remember to take a breath and drink some water.",
        "category": "wellness",
    },
    {
        "message": "No pressure at all, just sending some calm energy.",
        "category": "calm",
    },
    {
        "message": "Rooting for you and your small wins today!",
        "category": "encouragement",
    },
    {
        "message": "Your pod is here with you today.",
        "category": "solidarity",
    },
]


def ensure_default_templates():
    """
    Seeds pre-approved positive templates if none exist in the database.
    """
    if not NudgeTemplate.objects.exists():
        templates = [
            NudgeTemplate(message=t["message"], category=t["category"])
            for t in DEFAULT_TEMPLATES
        ]
        NudgeTemplate.objects.bulk_create(templates)
    return NudgeTemplate.objects.all()


def send_anonymous_nudge(sender, recipient_id, template_id):
    """
    Validates that sender and recipient belong to the same active Pod,
    validates the template is pre-approved, and creates the Nudge record.
    Returns (nudge, error_message).
    """
    try:
        recipient = User.objects.get(pk=recipient_id)
    except (User.DoesNotExist, ValueError):
        return None, "Selected pod member could not be found."

    if sender == recipient:
        return None, "You cannot send a nudge to yourself."

    try:
        template = NudgeTemplate.objects.get(pk=template_id)
    except (NudgeTemplate.DoesNotExist, ValueError):
        return None, "Please select an approved encouragement template."

    # Validate shared active pod
    sender_pods = set(
        PodMembership.objects.filter(user=sender, status="active").values_list("pod_id", flat=True)
    )
    recipient_membership = (
        PodMembership.objects.filter(user=recipient, status="active", pod_id__in=sender_pods)
        .select_related("pod")
        .first()
    )

    if not recipient_membership:
        return None, "You can only send nudges to members within your active pod."

    nudge = Nudge.objects.create(
        pod=recipient_membership.pod,
        sender=sender,
        recipient=recipient,
        template=template,
    )
    return nudge, None


def get_unread_nudges_for_user(user):
    """
    Retrieves unread nudges addressed to the given user.
    """
    if not user.is_authenticated:
        return Nudge.objects.none()
    return Nudge.objects.filter(recipient=user, is_read=False).select_related("template", "pod").order_by("-sent_at")


def mark_nudge_read(user, nudge_id):
    """
    Marks a specific nudge as read if it belongs to the user.
    """
    updated_count = Nudge.objects.filter(id=nudge_id, recipient=user, is_read=False).update(is_read=True)
    return updated_count > 0

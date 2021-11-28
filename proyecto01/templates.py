from spade.template import Template
from spade.message import Message


def make_message(template: Template, **kwargs) -> Message:
    """
    Makes a messsage from a template.
    :param template: template to create message from
    :param kwargs: fields of the message to overwrite the template ones
    :return: message created from template
    """
    def from_template_or_kwargs(attrname):
        try:
            return kwargs[attrname]
        except KeyError:
            return getattr(template, attrname, None)

    return Message(
        sender=from_template_or_kwargs('sender'),
        to=from_template_or_kwargs('to'),
        body=from_template_or_kwargs('body'),
        thread=from_template_or_kwargs('thread'),
        metadata=from_template_or_kwargs('metadata')
    )


def make_reply(msg: Message, template: Template) -> Message:
    """
    Creates a message from a template and switched sender and receipent of an original message.
    :param msg: message to make reply for
    :param template: template of the messsage
    :return: message created from template with switched sender and receipent
    """
    return make_message(template, to=str(msg.sender), sender=str(msg.to))


# alias
def make_template(*args, **kwargs):
    """
    Alias for spade.template.Template.
    """
    return Template(*args, **kwargs)


def make_metadata_with_body_template(performative: str, ontology: str, body: str) -> Template:
    """
    Makes template with performative and ontology metadata easily.
    """
    return Template(metadata=dict(
        performative=performative,
        ontology=ontology
        ),
        body=body
    )


def make_metadata_template(performative: str, ontology: str) -> Template:
    """
    Makes template with performative and ontology metadata easily.
    """
    return Template(metadata=dict(
        performative=performative,
        ontology=ontology
        )
    )


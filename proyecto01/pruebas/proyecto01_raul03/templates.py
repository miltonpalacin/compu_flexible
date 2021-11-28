from spade.template import Template
from spade.message import Message


def make_message(template: Template, **kwargs) -> Message:
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
    return make_message(template, to=str(msg.sender), sender=str(msg.to))


def make_template(*args, **kwargs):
    return Template(*args, **kwargs)


def join_network_template(body='') -> Template:
    return make_general_template('joinNetwork', 'join', body)


def request_file_template(body='') -> Template:
    return make_general_template('requestFile', 'request', body)


def request_file_agent_list_template(body='') -> Template:
    return make_general_template('requestFileAgentsList', 'request', body)


def receive_agent_list_template(body='') -> Template:
    return make_general_template('receiveAgentList', 'request', body)


def send_file_template(body='') -> Template:
    return make_general_template('sendFile', 'data', body)


def receive_file_template(body='') -> Template:
    return make_general_template('receiveFile', 'data', body)


def file_list_request_template(body='') -> Template:
    return make_general_template('fileListRequest', 'request', body)


def file_list_response_template(body='') -> Template:
    return make_general_template('fileListResponse', 'request', body)


def update_file_list_template(body='') -> Template:
    return make_general_template('addDownloadedFile', 'request', body)


def make_general_template(performative, ontology, body) -> Template:
    if body == '':
        return Template(metadata=dict(
            performative=performative,
            ontology=ontology
            )
        )

    return Template(metadata=dict(
        performative=performative,
        ontology=ontology
        ),
        body=body
    )
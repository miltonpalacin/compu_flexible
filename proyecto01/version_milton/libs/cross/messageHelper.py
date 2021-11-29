from spade.template import Template
from spade.message import Message
import base64
from ast import literal_eval
import os


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


def files_register_template(body='') -> Template:
    return make_general_template('filesRegister', 'register', body)


def public_confirm_template(body='') -> Template:
    return make_general_template('publicComfirm', 'response', body)


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


def request_cpu_template(body='') -> Template:
    return make_general_template('requestCpu', 'request', body)


def receive_cpu_template(body='') -> Template:
    return make_general_template('receiveCpu', 'request', body)


def request_cpu_exec_template(body='') -> Template:
    return make_general_template('requestCpuExec', 'request', body)


def receive_cpu_result_template(body='') -> Template:
    return make_general_template('receiveCpuResult', 'request', body)


def receive_cpu_per_template(body='') -> Template:
    return make_general_template('receiveCpuPer', 'request', body)


def response_cpu_per_template(body='') -> Template:
    return make_general_template('requestCpuPer', 'request', body)

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


def encode_array(data):
    msg = repr(data)
    msg = msg.encode('utf-8')
    msg = base64.b64encode(msg)
    msg = msg.decode('ascii')
    return msg


def decode_array(msg):
    data = msg.encode('ascii')
    data = base64.b64decode(msg)
    data = data.decode('utf-8')
    return literal_eval(data)


def encode_file(filename, path):
    with open(path, "rb") as f:
        content = f.read()
        base64_bytes = base64.b64encode(content)
        content = base64_bytes.decode('ascii') + "[|filename|]" + filename
    return content


def decode_file(path, content_text):
    contents = content_text.split("[|filename|]")
    filename = contents[1]
    file_path = os.path.join(path, filename)
    with open(file_path, "wb") as f:
        base64_bytes = contents[0].encode('ascii')
        content = base64.b64decode(base64_bytes)
        f.write(content)


import settings


def get_task_hand_way(access_way):
    task_type = settings.task_type.capitalize() + "Obj"
    task_module = __import__("PacketRequest." + task_type, globals(), locals(), [task_type])
    up_access = getattr(task_module, task_type)
    return getattr(up_access(), access_way)


from fastapi import Header

def userid(x_vsc_machine_id: str = Header("anonymous")) -> str:
    return x_vsc_machine_id
def decode(can_id, data):

    bytes_list = [int(x, 16) for x in data.split()]

    if can_id == "0x100":
        return {
            "type": "speed",
            "value": bytes_list[0]
        }

    if can_id == "0x200":
        return {
            "type": "fuel",
            "value": bytes_list[1]
        }

    if can_id == "0x300":
        return {
            "type": "temp",
            "value": bytes_list[0] + 40
        }

    return {
        "type": "unknown",
        "value": 0
    }
import json
import time
import random
import math
import copy

from .genpy.player_brain_pb2_grpc import PlayerBrainStub
from .genpy.player_brain_pb2 import RequestObservation, RequestAction, Request
from .genpy.common_pb2 import Field, Entity
import grpc


class PlayerBrainClient:
    def __init__(self, host, port):
        conn = grpc.insecure_channel(f'{host}:{port}')
        self.__client  = PlayerBrainStub(channel=conn)

    def request_action(self, action):
        req = Request()
        req.action.CopyFrom(action)
        return self.__client.RpcCall(req)

    def request_observation(self):
        req = Request()
        req.observation.CopyFrom(RequestObservation())
        return self.__client.RpcCall(req)
    
    def ping(self):
        req = Request()
        return self.__client.RpcCall(req)

class UETestClient:
    def __init__(self, host, port):
        self.client = PlayerBrainClient(host, port)
        self.client.ping()

    def reset(self):
        action = RequestAction()
        print("action is ", action)
        entities_fields = action.request.fields.add()
        entities_fields.name = "reset"
        ret = self.client.request_action(action)
        print("ret is ", ret)
        time.sleep(3)
        response = self.decode(ret.action.observation)
        return {"reset": "ok"}

    def obs(self):
        ret = self.client.request_observation()
        print("ret is ", ret)
        response = self.decode(ret.observation.observation)
        return {"observation": response}

    def execute(self, eval_data):
        if eval_data.get("command", None) == 'reset':
            return self.reset() 
        elif eval_data.get("command", None) == 'observation':
            return self.obs() 
        request = self.encode(eval_data)
        ret = self.client.request_action(RequestAction(request=request))
        response = self.decode(ret.action.observation)
        return response

    def decode(self, item):
        if isinstance(item, Entity):
            k = item.name 
            v = {}
            for ent in item.entities:
                p,j = self.decode(self, ent)
                v[p] = j
            for fld in item.fields:
                p,j = self.decode(self, fld)
                v[p] = j
            if k == "":
                return v
            else:
                return k, v
        elif isinstance(item, Field):
            k = item.name
            if item.type in [0, 1]:
                v = item.iv
            elif item.type in [2, 3]:
                v = item.dv
            elif item.type in [4, 5]:
                v = item.bv
            return k, v

    def encode(self, eval_data):
        request = self.auto_gen("", eval_data)
        return request

    def auto_gen(self, name, obj):
        if isinstance(obj, dict):
            entity = Entity()
            entity.name = name
            for k, v in obj.items():
                item = self.auto_gen(k, v)
                if isinstance(item, Entity):
                    entity.entities.append(entity)
                elif isinstance(item, Field):
                    entity.fields.append(item)
            return entity
        else:
            field = self.gen_field(name, obj)
            return field

    def gen_field(self, k, v):
        field = Field()
        field.name = k
        if type(v) != list:
            v = [v]
        v_it = v[0]
        if isinstance(v_it, int):
            field.type = 0 if len(v)==1 else 1
            field.iv.extend(v)
        elif isinstance(v_it, float):
            field.type = 2 if len(v)==1 else 3
            field.dv.extend(v)
        elif isinstance(v_it, str):
            field.type = 4 if len(v)==1 else 5
            field.bv.extend([bytes(it, encoding='utf8') for it in v if len(it)])
        else :
            print(f"Error Types, key: {k} type of v is {type(v_it)}")
            exit()
        return field

def execute():
    import os
    host = os.popen("cat /etc/resolv.conf |grep nameserver |awk '{print $2}'").read().strip()
    client = RenderClient("172.1.1.84", "60060")


if __name__ == '__main__':
    while True:
        if 1:
            execute()
        #except:
            time.sleep(5)

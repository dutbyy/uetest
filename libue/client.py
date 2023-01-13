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
        print("exec obs")
        ret = self.client.request_observation()
        print("ret is ", ret.observation.observation)
        _, response = self.decode(ret.observation.observation)
        print('***************************************************')
        print(response)
        print('***************************************************')
        return {"observation": response}

    def execute(self, eval_data):
        print("execute: ", eval_data)
        if eval_data.get("command", None) == 'reset':
            return self.reset() 
        elif eval_data.get("command", None) == 'observation':
            return self.obs() 
        print("before encode")
        request = self.encode(eval_data)
        print("----------request----------")
        print(request)
        print("----------request----------")

        ret = self.client.request_action(RequestAction(request=request))
        response = self.decode(ret.action.observation)
        print("----------response----------")
        print(ret)
        print("----------response----------")
        return response

    def decode(self, item):
        if isinstance(item, Field):
            print("field: ", item.name)
            k = item.name
            if item.type in [0, 1]:
                v = list(item.iv)
                v = v[0] if len(v)==1 else v 
            elif item.type in [2, 3]:
                v = list(item.dv)
                v = v[0] if len(v)==1 else v 
            elif item.type in [4, 5]:
                v = item.bv.__str__()
            return k, v
        elif isinstance(item, Entity):
            print("entity: ", item.name)
            k = item.name 
            v = {}
            for ent in item.entities:
                p,j = self.decode(ent)
                if p == "":
                    p = 'entities'
                if p not in v:
                    v[p] = []
                v[p].append(j)
            for fld in item.fields:
                p,j = self.decode(fld)
                v[p] = j
            if k == "":
                return "", v
            else:
                return k, v
        

    def encode(self, eval_data):
        request = self.auto_gen("", eval_data)
        print("encode over", request)
        return request

    def auto_gen(self, name, obj):
        print(f'auto gen {name}: {obj}')
        if isinstance(obj, dict):
            entity = Entity()
            entity.name = name
            for k, v in obj.items():
                item = self.auto_gen(k, v)
                if isinstance(item, Entity):
                    print('item is Entity', item.name)
                    entity.entities.append(item)
                    print('item Entity append finished')
                elif isinstance(item, Field):
                    print('item is Field', item.name)
                    entity.fields.append(item)
            print(entity)
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
            # exit()
            # exit()
        # print(field)
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

from pytezos import pytezos, Key 


dataset = {
    
    "f427452d017d150":{"path":"/app/key/rl.json"},

    "a8a63149c45c90d":{"path":"/app/key/hm.json"},

    "90afc1e178dee46":{"path":"/app/key/hm.json"}

}

def GetBalance(Id):
    key = Key.from_faucet(dataset[Id]['path'])
    global pytezos
    pytezos = pytezos.using(key=key)
    return pytezos.account()

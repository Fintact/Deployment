from pytezos import pytezos, Key


dataset = {
    "f427452d017d150": "/app/key/tz1NJNr9BweMzGgqVFfu82pvGwAci1KjGanK.json",
    "a8a63149c45c90d": "/app/key/tz1SJ7dB1iXPb1C1ii93CGpKsCwzWkuRBVpJ.json",
}


def GetBalance(Id):
    key = Key.from_faucet(dataset[Id])
    global pytezos
    pytezos = pytezos.using(key=key)
    return pytezos.account()


def Payment(sender, reciever, amt):
    global pytezos, Key

    sender_key = Key.from_faucet(dataset[sender])
    reciever_key = Key.from_faucet(dataset[reciever])

    sender_account = pytezos.using(key=sender_key)
    reciever_account = pytezos.using(key=reciever_key)

    print(sender_account.key.public_key_hash(), reciever_account.key.public_key_hash())
    print(
        sender_account.transaction(
            destination=reciever_account.key.public_key_hash(), amount=int(amt)
        )
        .autofill()
        .json_payload()
    )
    print(
        sender_account.transaction(
            destination=reciever_account.key.public_key_hash(), amount=int(amt)
        )
        .autofill()
        .sign()
        .preapply()
    )

    output = (
        sender_account.transaction(
            destination=reciever_account.key.public_key_hash(), amount=int(amt)
        )
        .autofill()
        .sign()
        .inject()
    )
    return output


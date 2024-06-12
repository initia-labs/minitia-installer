def template_env():
    template = """
TYPEORM_CONNECTION=postgres               # database connection (currently only support `postgres`)
TYPEORM_HOST=localhost                    # database host
TYPEORM_USERNAME=username                 # database username
TYPEORM_PASSWORD=password                 # database password
TYPEORM_DATABASE=rollup                   # database name
TYPEORM_PORT=5432                         # database port
TYPEORM_SYNCHRONIZE=true                  # synchronize database schema
TYPEORM_LOGGING=false                     # enable logging
TYPEORM_ENTITIES=dist/orm/*Entity.js      # entity path

L1_CHAIN_ID=initiation-1
L2_CHAIN_ID=local-minitia
L1_LCD_URI=https://lcd.initiation-1.initia.xyz
L1_RPC_URI=https://rpc.initiation-1.initia.xyz
L2_LCD_URI=http://127.0.0.1:1317
L2_RPC_URI=http://127.0.0.1:26657
BRIDGE_ID=1
"""
    return template


def create_executor_env():
    mneonic = "tent apple ... "
    template = template_env()
    template += f"""
EXECUTOR_PORT=5000
ENABLE_ORACLE=true
EXECUTOR_MNEMONIC='{mneonic}'
"""
    with open(".env.executor", "w") as f:
        f.write(template)


def create_opinit_bots_env():
    create_executor_env()


if __name__ == "__main__":
    create_opinit_bots_env()

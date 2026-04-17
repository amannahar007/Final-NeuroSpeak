import asyncio
import random
import time

async def handle_client(reader, writer):
    print("Dummy ESP32: New connection")
    try:
        while True:
            # Let's send a fake burst of records to trigger the rules engine
            # We want to trigger WATER: jaw(1000-2500), chin(500-2000), ear(1000-3000)
            # STATS:j_env,j_avg,j_min,j_max,c_env,c_avg,c_min,c_max,e_env,e_avg,e_min,e_max,btn,ts
            # First, send 512 samples of a word match
            for _ in range(512):
                j_env = random.randint(1200, 1800)
                c_env = random.randint(1200, 1800)
                e_env = random.randint(1200, 1800)
                writer.write(f"STATS:{j_env},{j_env},{j_env},{j_env},{c_env},{c_env},{c_env},{c_env},{e_env},{e_env},{e_env},{e_env},0,123456\n".encode())
                await writer.drain()
                await asyncio.sleep(0.001)
            print("Finished burst")
            await asyncio.sleep(5)
    except Exception as e:
        print(e)
        pass

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8080)
    print("Dummy ESP32 TCP Server listening on 127.0.0.1:8080")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())

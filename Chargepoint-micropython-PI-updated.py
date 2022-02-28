import asyncio
import logging
import random
#import machine
#button = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)



import websockets
from datetime import datetime
from ocpp.v16 import call
from ocpp.v16.enums import AuthorizationStatus
from ocpp.v16 import ChargePoint as cp
from ocpp.routing import on
from ocpp.v16.enums import Action, AuthorizationStatus, RemoteStartStopStatus
from datetime import datetime
from ocpp.v16 import call
from ocpp.v16.enums import AuthorizationStatus
from ocpp.v16 import ChargePoint as cp
from ocpp.routing import on
from ocpp.v16.enums import Action, AuthorizationStatus, RemoteStartStopStatus, ConfigurationStatus, ReservationStatus, AvailabilityType, AvailabilityStatus
from ocpp.v16 import call_result
from enums import ConfigurationKey as ck

logging.basicConfig(level=logging.INFO)

reserved_Id_code = []
reserved_Id = []
local_auth_list = ["test_cp2", "test_cp3", 11]
connector_available = [1, 2, 3]
connector_in_use = [5, 6]
config_settings = {"1": {"key": ck.authorize_remote_tx_requests, "readonly": True, "value": True}}
# get local machine name
authorization_cache = []


# connection to hostname on the port.


class ChargePoint(cp):

    async def authorize(self):
        await asyncio.sleep(1)

        while True:
            a=input(" Press y to begin authorization process")
            if a=="y":
                print('Button pressed!')
                id = input("Enter authentication password")  # id = test_cp5 for reserve process and test_cp2 for simple start TX

                r = call.AuthorizePayload(id_tag=id)
                response1 = await self.call(r)

                if response1.id_tag_info['status'] == 'Accepted':
                    print("authorized.")
                    dic = {id: "Accepted"}
                    # start bulb
                    authorization_cache.append(dic)
                    print(authorization_cache)

                    if id in reserved_Id:

                        #read voltage of starting meter value and store in variable
                        #use this variable to store in meter start

                        sdadd = call.StartTransactionPayload(connector_id=2,
                                                             id_tag=id, meter_start=12,
                                                             timestamp=datetime.utcnow().isoformat(),
                                                             reservation_id=reserved_Id_code[0])

                        response12 = await self.call(sdadd)
                        if response12.id_tag_info['status'] == 'Accepted':
                            print("Charging now")
                            tid = response12.transaction_id
                            for j in range(0, 7):
                                await asyncio.sleep(2)
                                print("Charging")

                            sdadd2 = call.StopTransactionPayload(meter_stop=200,
                                                                 timestamp=datetime.utcnow().isoformat(),
                                                                 transaction_id=tid)
                            response123 = await self.call(sdadd2)


                        else:
                            print('transaction failed')

                    else:
                        sdadd = call.StartTransactionPayload(connector_id=2,
                                                             id_tag=id, meter_start=12,
                                                             timestamp=datetime.utcnow().isoformat(), reservation_id=0)

                        response12 = await self.call(sdadd)
                        if response12.id_tag_info['status'] == 'Accepted':
                            print("Charging now")
                            tid = response12.transaction_id
                            for j in range(0, 7):
                                await asyncio.sleep(2)
                                print("Charging")
                                #    *send meter values*
                                # while meter/bulb on
                                # read voltage
                                # send meter val
                                # stop bulb

                            sdadd2 = call.StopTransactionPayload(meter_stop=200,
                                                                 timestamp=datetime.utcnow().isoformat(),
                                                                 transaction_id=tid)

                            response123 = await self.call(sdadd2)
                        else:
                            print('transaction failed')

                else:
                    dic = {id: "Rejected"}
                    authorization_cache.append(dic)
                    print("Not Authorized")




            else:
                pass

    async def send_heartbeat(self):
        req = call.HeartbeatPayload()
        res = await self.call(req)

        print("current time received from CMS, ", res.current_time)

    async def send_boot_notification(self):
        request = call.BootNotificationPayload(
            charge_point_model="Optimus", charge_point_vendor="The Mobility"
        )
        response = await self.call(request)

        if response.status == 'Accepted':
            print("Boot confirmed.")

    @on(Action.ChangeConfiguration)
    async def on_change_config(self, key, value):
        if key == "authorize_remote_tx_requests":
            config_settings['1']['value'] = value
            print(config_settings)
            return call_result.ChangeConfigurationPayload(status=ConfigurationStatus.accepted)

        else:
            print("config rejected")
            return call_result.ChangeConfigurationPayload(status=ConfigurationStatus.rejected)

    @on(Action.RemoteStartTransaction)
    async def remote_start_transaction(self, id_tag):
        print("Charging started remotely by CMS")

        if id_tag in local_auth_list:

            return call_result.RemoteStartTransactionPayload(status=RemoteStartStopStatus.accepted)

        else:
            return call_result.RemoteStartTransactionPayload(status=RemoteStartStopStatus.rejected)
            print("stopped charging")

    @on(Action.RemoteStopTransaction)
    async def remote_stop_transaction(self, transaction_id):

        if transaction_id in local_auth_list:

            return call_result.RemoteStartTransactionPayload(status=RemoteStartStopStatus.accepted)

        else:
            return call_result.RemoteStartTransactionPayload(status=RemoteStartStopStatus.rejected)

    @on(Action.UpdateFirmware)
    async def on_firmware_update(self, location, retrieve_date):
        print("Chargepoint will download firmware from portal ", location, "after ", retrieve_date)
        return call_result.UpdateFirmwarePayload()

    @on(Action.ReserveNow)
    async def on_reserve(self, connector_id, expiry_date, id_tag, reservation_id):
        print("reservation process started")
        reserved_Id.append(id_tag)
        reserved_Id_code.append(reservation_id)
        if connector_id in connector_available:
            hi = connector_available.index(connector_id)
            print("connector no, ", connector_id, " is reserved till ", expiry_date, "for id tag ", id_tag)
            connector_available.pop(hi)

            return call_result.ReserveNowPayload(status=ReservationStatus.accepted)
        elif connector_id == 0:
            print("connector no ", random.choice(connector_available), "is reserved", " for id tag", id_tag)
            return call_result.ReserveNowPayload(status=ReservationStatus.accepted)

        else:
            return call_result.ReserveNowPayload(status=ReservationStatus.occupied)

    @on(Action.ChangeAvailability)
    async def on_change_availability(self, connector_id, type):
        if connector_id in connector_available:
            if type == AvailabilityType.inoperative:
                i = connector_available.index(connector_id)
                connector_available.pop(i)
                print(connector_available)
                return call_result.ChangeAvailabilityPayload(status=AvailabilityStatus.accepted)
            else:
                return call_result.ChangeAvailabilityPayload(status=AvailabilityStatus.accepted)

        elif connector_id in connector_in_use:
            return call_result.ChangeAvailabilityPayload(status=AvailabilityStatus.scheduled)

        else:
            return call_result.ChangeAvailabilityPayload(status=AvailabilityStatus.rejected)


async def main():
    async with websockets.connect(
            'ws://localhost:9005/CP_6',
            subprotocols=['ocpp1.6'],ping_interval=None
    ) as ws:



        cp = ChargePoint('CP_6', ws)

        await asyncio.gather(cp.start(), cp.send_boot_notification(), cp.send_heartbeat(),cp.authorize())







if __name__ == '__main__':
    asyncio.run(main())

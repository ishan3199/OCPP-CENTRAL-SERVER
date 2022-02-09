############## Dependencies  ############


import asyncio
import logging
import websockets
from datetime import datetime,timedelta
import random
import os
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import MessageTrigger, ChargingProfileKindType, \
    ChargingProfileStatus, ChargingRateUnitType, ClearChargingProfileStatus, \
    ChargePointStatus,ChargingProfilePurposeType, Action, AuthorizationStatus, \
    RemoteStartStopStatus,ReservationStatus,AvailabilityType,\
    AvailabilityStatus,ConfigurationStatus,ClearCacheStatus
from enums import OcppMisc as oc
from enums import ConfigurationKey as ck
from ocpp.v16 import call_result,call



############## Data Structures for storage and Logging initiation  #############


reserved_ID=[]
current_connected_chargepoints={}
connected_chargepoint = []
config_settings={"key":ck.authorize_remote_tx_requests, "readonly": True,"value":True}

logging.basicConfig(level=logging.INFO)





############  OCPP Protocol Chargepoint Class  ###################


class ChargePoint(cp):

    @on(Action.StatusNotification)
    async def on_status(self,connector_id,error_code,status,**kwargs):

        print(status)
        return call_result.StatusNotificationPayload()


    @on(Action.MeterValues)
    async def on_meter(self,meter_value,connector_id,**kwargs):
        print(meter_value)
        return call_result.MeterValuesPayload()

    @on(Action.Authorize)
    async def on_auth(self,id_tag,**kwargs):
        if id_tag == "test_cp2" or id_tag == "test_cp5":
            print("authorized")
            return call_result.AuthorizePayload(
                id_tag_info={oc.status.value: AuthorizationStatus.accepted.value}
            )
        else:
            print("Not Authorized")
            return call_result.AuthorizePayload(
                id_tag_info={oc.status.value: AuthorizationStatus.invalid.value}
            )

    @on(Action.BootNotification)
    async def on_boot_notification(self, charge_point_model,charge_point_vendor, **kwargs):

        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status='Accepted'
        )


    @on(Action.StartTransaction)
    async def on_startTX(self,id_tag,connector_id, meter_start, timestamp, reservation_id, **kwargs):
        print("session for user", id_tag)

        if reservation_id != 0:

            if reservation_id in reserved_ID:
                print("reservation ended for ,", reservation_id)
                if id_tag == "test_cp2" or id_tag == "test_cp5":
                    print("valid transaction for connector, ", connector_id)
                    print("meter value at start of transaction ", meter_start)
                    return call_result.StartTransactionPayload(
                        transaction_id=random.randint(122, 6666666666),
                        id_tag_info={oc.status.value: AuthorizationStatus.accepted.value}
                    )
                else:
                    print("Not Authorized transaction")
                    return call_result.StartTransactionPayload(
                        transaction_id=0, id_tag_info={oc.status.value: AuthorizationStatus.invalid.value}
                    )
            else:
                print("error")

        else:

            if id_tag == "test_cp2" or id_tag == "test_cp5":
                print("valid transaction for connector, ", connector_id)
                print("meter value at start of transaction ", meter_start)
                return call_result.StartTransactionPayload(
                    transaction_id=random.randint(122, 6666666666),
                    id_tag_info={oc.status.value: AuthorizationStatus.accepted.value}
                )
            else:
                print("Not Authorized transaction")
                return call_result.StartTransactionPayload(
                    transaction_id=0, id_tag_info={oc.status.value: AuthorizationStatus.invalid.value}
                )



    @on(Action.StopTransaction)
    async def on_stopTX(self,meter_stop,timestamp,transaction_id, **kwargs):
        print("Transaction stopped at value", meter_stop, " for transaction id", transaction_id,"at", timestamp)
        return call_result.StopTransactionPayload(
            None
        )

    @on(Action.Heartbeat)
    async def on_HB(self):
        print("heart beat received from chargepoint, ", connected_chargepoint[-1])
        return call_result.HeartbeatPayload(current_time=datetime.utcnow().isoformat())



    async def UpdateFirmware(self):
        dates = datetime.today() + timedelta(days=2)
        firm = call.UpdateFirmwarePayload(location="URL-FOR-FIRMWARE-DOWNLOAD", retrieve_date = datetime.utcfromtimestamp(1639056285).isoformat())
        send=await self.call(firm)


    async def remote_start_transaction(self):

        request = call.RemoteStartTransactionPayload( id_tag="test_cp2")
        response = await self.call(request)
        if response.status == RemoteStartStopStatus.accepted:
            print("Transaction Started!!! remotely with authentication")
        else:
            print("Something went wrong!!")


    async def setChargingProfile(self):
        req = call.SetChargingProfilePayload(
            connector_id=0,
            cs_charging_profiles={
                oc.charging_profile_id.value: 8,
                oc.stack_level.value: 0,
                oc.charging_profile_kind.value: ChargingProfileKindType.recurring.value,
                oc.charging_profile_purpose.value: ChargingProfilePurposeType.charge_point_max_profile.value,
                oc.charging_schedule.value: {
                    oc.charging_rate_unit.value: ChargingRateUnitType.watts,
                    oc.charging_schedule_period.value: [
                        {oc.start_period.value: 0, oc.limit.value: 100}
                    ],
                },
            },
        )
        response = await self.call(req)
        if response.status == ChargingProfileStatus.accepted:
            print("Charge profile accepted")


    async def remote_stop_transaction(self):

        request = call.RemoteStopTransactionPayload(
            transaction_id=11
        )
        response = await self.call(request)
        if response.status == RemoteStartStopStatus.accepted:
            print("Transaction Stopped!!! remotely with authentication")
        else:
            print("error")


    async def remote_trigger(self):
        request = call.TriggerMessagePayload(requested_message= MessageTrigger.boot_notification, connector_id=1)
        response = await self.call(request)



    async def change_config(self):
        request = call.ChangeConfigurationPayload(key="authorize_remote_tx_requests",value="True")
        response = await self.call(request)
        if response.status == ConfigurationStatus.accepted:
            print("configuration change applied")

        elif response.status == ConfigurationStatus.reboot_required:
            print("change successful but reboot required")
        else:
            print("change unsuccessful")



    async def clearcache(self):
        request = call.ClearCachePayload(


        )
        response = await self.call(request)
        if response.status == ClearCacheStatus.accepted:
            print("Cache cleared")

        if response.status == ClearCacheStatus.rejected:
            print("cache not cleared")


    async def reservenow(self):

        reservation_id=1 # any id other than 0
        reserved_ID.append(reservation_id)
        request = call.ReserveNowPayload(
            connector_id=2,expiry_date=datetime.utcfromtimestamp(1639056288).isoformat(),id_tag="test_cp5",
            reservation_id=reservation_id
        )
        response = await self.call(request)
        if response.status == ReservationStatus.accepted:
            print("reservation accepted for connector 1 ")

        if response.status == ReservationStatus.occupied:
            print("all connectors are busy")

    async def change_availability(self):
        request = call.ChangeAvailabilityPayload(
            connector_id=1,type=AvailabilityType.inoperative
        )
        response = await self.call(request)
        if response.status == AvailabilityStatus.accepted:
            print("availabilty change applied successfully")

        if response.status == AvailabilityStatus.rejected:
            print("availabilty change not applied")
        if response.status == AvailabilityStatus.scheduled:
            print("availabilty change will be applied soon")







############ ON_CONNECT HANDLER FOR WEB SOCKET INCOMING CONNECTIONS #######################


async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers[
            'Sec-WebSocket-Protocol']
    except KeyError:
        logging.info("Client hasn't requested any Subprotocol. "
                 "Closing Connection")
    if websocket.subprotocol:
        print(path)
        print(websocket)

        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
                        ' but client supports  %s | Closing connection',
                        websocket.available_subprotocols,
                        requested_protocols)


        return await websocket.close()

    charge_point_id = path.strip('/')
    try:
        #for change_Availablity
        if charge_point_id == 'CP_3':

            current_connected_chargepoints[path] = websocket
            connected_chargepoint.append(charge_point_id)
            print("Valid Chargepoint")
            cp = ChargePoint(charge_point_id, websocket)
            print(current_connected_chargepoints)

            await asyncio.gather(cp.start(),cp.change_availability())

        # for remote start
        elif charge_point_id == 'CP_4':
            current_connected_chargepoints[path] = websocket
            connected_chargepoint.append(charge_point_id)
            print("Valid Chargepoint")
            print(current_connected_chargepoints)
            cp = ChargePoint(charge_point_id, websocket)

            await asyncio.gather(cp.start(),cp.change_config(),cp.remote_start_transaction())




        elif charge_point_id == 'CP_7':

            print("Valid Chargepoint")
            current_connected_chargepoints[path] = websocket
            connected_chargepoint.append(charge_point_id)
            cp = ChargePoint(charge_point_id, websocket)

            await asyncio.gather(cp.start())

        # for start transaction
        elif charge_point_id == 'CP_6':
            current_connected_chargepoints[path] = websocket
            print("Valid Chargepoint")
            print(current_connected_chargepoints)
            connected_chargepoint.append(charge_point_id)
            cp = ChargePoint(charge_point_id, websocket)

            await asyncio.gather(cp.start())



        # for reserve
        elif charge_point_id == 'CP_5':
            current_connected_chargepoints[path] = websocket

            connected_chargepoint.append(charge_point_id)
            print("Valid Chargepoint")
            print(current_connected_chargepoints)
            cp = ChargePoint(charge_point_id, websocket)

            await asyncio.gather(cp.start(),cp.reservenow())


        else:
            print('Invalid chargepoint')


    except:
        pass




async def main():

    #port is defined as per heroku default port value taken from its environment

    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        port=int(os.environ["PORT"]),
        subprotocols=['ocpp1.6'],
        close_timeout=10,
        ping_interval=None
    )
    logging.info("WebSocket Server Started")
    await server.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
"""
Copyright (C) 2025 Interactive Brokers LLC. All rights reserved. This code is subject to the terms
 and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable.
"""

from ibapi.const import UNSET_DOUBLE
from ibapi.execution import ExecutionFilter

from ibapi.contract import Contract, DeltaNeutralContract, ComboLeg
from ibapi.order import Order
from ibapi.order_condition import OrderCondition, OperatorCondition, ContractCondition, PriceCondition, TimeCondition, MarginCondition, ExecutionCondition, VolumeCondition, PercentChangeCondition
from ibapi.tag_value import TagValue
from ibapi.utils import isValidIntValue, isValidFloatValue, isValidLongValue, isValidDecimalValue, decimalMaxString
from ibapi.order_condition import Create
from ibapi.common import TagValueList
from ibapi.order_cancel import OrderCancel

from ibapi.protobuf.ComboLeg_pb2 import ComboLeg as ComboLegProto
from ibapi.protobuf.Contract_pb2 import Contract as ContractProto
from ibapi.protobuf.DeltaNeutralContract_pb2 import DeltaNeutralContract as DeltaNeutralContractProto
from ibapi.protobuf.OrderCancel_pb2 import OrderCancel as OrderCancelProto
from ibapi.protobuf.OrderCondition_pb2 import OrderCondition as OrderConditionProto
from ibapi.protobuf.PlaceOrderRequest_pb2 import PlaceOrderRequest as PlaceOrderRequestProto
from ibapi.protobuf.CancelOrderRequest_pb2 import CancelOrderRequest as CancelOrderRequestProto
from ibapi.protobuf.GlobalCancelRequest_pb2 import GlobalCancelRequest as GlobalCancelRequestProto
from ibapi.protobuf.ExecutionFilter_pb2 import ExecutionFilter as ExecutionFilterProto
from ibapi.protobuf.ExecutionRequest_pb2 import ExecutionRequest as ExecutionRequestProto
from ibapi.protobuf.Order_pb2 import Order as OrderProto
from ibapi.protobuf.SoftDollarTier_pb2 import SoftDollarTier as SoftDollarTierProto
from ibapi.protobuf.AllOpenOrdersRequest_pb2 import AllOpenOrdersRequest as AllOpenOrdersRequestProto
from ibapi.protobuf.AutoOpenOrdersRequest_pb2 import AutoOpenOrdersRequest as AutoOpenOrdersRequestProto
from ibapi.protobuf.OpenOrdersRequest_pb2 import OpenOrdersRequest as OpenOrdersRequestProto
from ibapi.protobuf.CompletedOrdersRequest_pb2 import CompletedOrdersRequest as CompletedOrdersRequestProto
from ibapi.protobuf.ContractDataRequest_pb2 import ContractDataRequest as ContractDataRequestProto
from ibapi.protobuf.MarketDataRequest_pb2 import MarketDataRequest as MarketDataRequestProto
from ibapi.protobuf.CancelMarketData_pb2 import CancelMarketData as CancelMarketDataProto
from ibapi.protobuf.MarketDepthRequest_pb2 import MarketDepthRequest as MarketDepthRequestProto
from ibapi.protobuf.CancelMarketDepth_pb2 import CancelMarketDepth as CancelMarketDepthProto
from ibapi.protobuf.MarketDataTypeRequest_pb2 import MarketDataTypeRequest as MarketDataTypeRequestProto
from ibapi.protobuf.AccountDataRequest_pb2 import AccountDataRequest as AccountDataRequestProto
from ibapi.protobuf.ManagedAccountsRequest_pb2 import ManagedAccountsRequest as ManagedAccountsRequestProto
from ibapi.protobuf.PositionsRequest_pb2 import PositionsRequest as PositionsRequestProto
from ibapi.protobuf.CancelPositions_pb2 import CancelPositions as CancelPositionsProto
from ibapi.protobuf.AccountSummaryRequest_pb2 import AccountSummaryRequest as AccountSummaryRequestProto
from ibapi.protobuf.CancelAccountSummary_pb2 import CancelAccountSummary as CancelAccountSummaryProto
from ibapi.protobuf.PositionsMultiRequest_pb2 import PositionsMultiRequest as PositionsMultiRequestProto
from ibapi.protobuf.CancelPositionsMulti_pb2 import CancelPositionsMulti as CancelPositionsMultiProto
from ibapi.protobuf.AccountUpdatesMultiRequest_pb2 import AccountUpdatesMultiRequest as AccountUpdatesMultiRequestProto
from ibapi.protobuf.CancelAccountUpdatesMulti_pb2 import CancelAccountUpdatesMulti as CancelAccountUpdatesMultiProto
from ibapi.protobuf.HistoricalDataRequest_pb2 import HistoricalDataRequest as HistoricalDataRequestProto
from ibapi.protobuf.RealTimeBarsRequest_pb2 import RealTimeBarsRequest as RealTimeBarsRequestProto
from ibapi.protobuf.HeadTimestampRequest_pb2 import HeadTimestampRequest as HeadTimestampRequestProto
from ibapi.protobuf.HistogramDataRequest_pb2 import HistogramDataRequest as HistogramDataRequestProto
from ibapi.protobuf.HistoricalTicksRequest_pb2 import HistoricalTicksRequest as HistoricalTicksRequestProto
from ibapi.protobuf.TickByTickRequest_pb2 import TickByTickRequest as TickByTickRequestProto
from ibapi.protobuf.CancelHistoricalData_pb2 import CancelHistoricalData as CancelHistoricalDataProto
from ibapi.protobuf.CancelRealTimeBars_pb2 import CancelRealTimeBars as CancelRealTimeBarsProto
from ibapi.protobuf.CancelHeadTimestamp_pb2 import CancelHeadTimestamp as CancelHeadTimestampProto
from ibapi.protobuf.CancelHistogramData_pb2 import CancelHistogramData as CancelHistogramDataProto
from ibapi.protobuf.CancelTickByTick_pb2 import CancelTickByTick as CancelTickByTickProto

from ibapi.errors import (
    ERROR_ENCODING_PROTOBUF
)
from ibapi.utils import ClientException

@staticmethod
def createExecutionRequestProto(reqId: int, execFilter: ExecutionFilter) -> ExecutionRequestProto:
    executionFilterProto = ExecutionFilterProto()
    if isValidIntValue(execFilter.clientId): executionFilterProto.clientId = execFilter.clientId
    if execFilter.acctCode: executionFilterProto.acctCode = execFilter.acctCode
    if execFilter.time: executionFilterProto.time = execFilter.time
    if execFilter.symbol: executionFilterProto.symbol = execFilter.symbol
    if execFilter.secType: executionFilterProto.secType = execFilter.secType
    if execFilter.exchange: executionFilterProto.exchange = execFilter.exchange
    if execFilter.side: executionFilterProto.side = execFilter.side
    if isValidIntValue(execFilter.lastNDays): executionFilterProto.lastNDays = execFilter.lastNDays
    if execFilter.specificDates is not None and execFilter.specificDates: executionFilterProto.specificDates.extend(execFilter.specificDates)
    executionRequestProto = ExecutionRequestProto()
    if isValidIntValue(reqId): executionRequestProto.reqId = reqId
    executionRequestProto.executionFilter.CopyFrom(executionFilterProto)
    return executionRequestProto
 
@staticmethod
def createPlaceOrderRequestProto(orderId: int, contract: Contract, order: Order) -> PlaceOrderRequestProto:
    placeOrderRequestProto = PlaceOrderRequestProto()
    if isValidIntValue(orderId): placeOrderRequestProto.orderId = orderId
    contractProto = createContractProto(contract, order)
    if contractProto is not None: placeOrderRequestProto.contract.CopyFrom(contractProto)
    orderProto = createOrderProto(order)
    if orderProto is not None: placeOrderRequestProto.order.CopyFrom(orderProto)
    return placeOrderRequestProto

@staticmethod
def createContractProto(contract: Contract, order: Order) -> ContractProto:
    contractProto = ContractProto()
    if isValidIntValue(contract.conId): contractProto.conId = contract.conId
    if contract.symbol: contractProto.symbol = contract.symbol
    if contract.secType: contractProto.secType = contract.secType
    if contract.lastTradeDateOrContractMonth: contractProto.lastTradeDateOrContractMonth = contract.lastTradeDateOrContractMonth
    if isValidFloatValue(contract.strike): contractProto.strike = contract.strike
    if contract.right: contractProto.right = contract.right
    if contract.multiplier: contractProto.multiplier = float(contract.multiplier)
    if contract.exchange: contractProto.exchange = contract.exchange
    if contract.primaryExchange: contractProto.primaryExch = contract.primaryExchange
    if contract.currency: contractProto.currency = contract.currency
    if contract.localSymbol: contractProto.localSymbol = contract.localSymbol
    if contract.tradingClass: contractProto.tradingClass = contract.tradingClass
    if contract.secIdType: contractProto.secIdType = contract.secIdType
    if contract.secId: contractProto.secId = contract.secId
    if contract.includeExpired: contractProto.includeExpired = contract.includeExpired
    if contract.comboLegsDescrip: contractProto.comboLegsDescrip = contract.comboLegsDescrip
    if contract.description: contractProto.description = contract.description
    if contract.issuerId: contractProto.issuerId = contract.issuerId

    comboLegProtoList = createComboLegProtoList(contract, order)
    if comboLegProtoList is not None and comboLegProtoList: contractProto.comboLegs.extend(comboLegProtoList)

    deltaNeutralContractProto = createDeltaNeutralContractProto(contract)
    if deltaNeutralContractProto is not None: contractProto.deltaNeutralContract.CopyFrom(deltaNeutralContractProto)

    return contractProto

@staticmethod
def createDeltaNeutralContractProto(contract: Contract) -> DeltaNeutralContractProto:
    deltaNeutralContractProto = None
    if contract.deltaNeutralContract is not None:
        deltaNeutralContract = contract.deltaNeutralContract
        deltaNeutralContractProto = DeltaNeutralContractProto()
        if isValidIntValue(deltaNeutralContract.conId): deltaNeutralContractProto.conId = deltaNeutralContract.conId
        if isValidFloatValue(deltaNeutralContract.delta): deltaNeutralContractProto.delta = deltaNeutralContract.delta
        if isValidFloatValue(deltaNeutralContract.price): deltaNeutralContractProto.price = deltaNeutralContract.price
    return deltaNeutralContractProto


@staticmethod
def createComboLegProtoList(contract: Contract, order: Order) -> list[ComboLegProto]:
    comboLegs = contract.comboLegs
    orderComboLegs = order.orderComboLegs if order is not None else None 
    comboLegProtoList = []
    if comboLegs is not None and comboLegs:
        for i, comboLeg in enumerate(comboLegs):
            perLegPrice = UNSET_DOUBLE
            if orderComboLegs is not None and i < len(orderComboLegs):
                perLegPrice = orderComboLegs[i].price
            comboLegProto = createComboLegProto(comboLeg, perLegPrice)
            comboLegProtoList.append(comboLegProto)
    return comboLegProtoList

@staticmethod
def createComboLegProto(comboLeg: ComboLeg, perLegPrice: float) -> ComboLegProto:
    comboLegProto = ComboLegProto()
    if isValidIntValue(comboLeg.conId): comboLegProto.conId = comboLeg.conId
    if isValidIntValue(comboLeg.ratio): comboLegProto.ratio = comboLeg.ratio
    if comboLeg.action: comboLegProto.action = comboLeg.action
    if comboLeg.exchange: comboLegProto.exchange = comboLeg.exchange
    if isValidIntValue(comboLeg.openClose): comboLegProto.openClose = comboLeg.openClose
    if isValidIntValue(comboLeg.shortSaleSlot): comboLegProto.shortSalesSlot = comboLeg.shortSaleSlot
    if comboLeg.designatedLocation: comboLegProto.designatedLocation = comboLeg.designatedLocation
    if isValidIntValue(comboLeg.exemptCode): comboLegProto.exemptCode = comboLeg.exemptCode
    if isValidFloatValue(perLegPrice): comboLegProto.perLegPrice = perLegPrice
    return comboLegProto

@staticmethod
def createOrderProto(order: Order) -> OrderProto:
    orderProto = OrderProto()
    if isValidIntValue(order.clientId): order.clientId = order.clientId
    if isValidLongValue(order.permId): orderProto.permId = order.permId
    if isValidIntValue(order.parentId): orderProto.parentId = order.parentId
    if order.action: orderProto.action = order.action
    if isValidDecimalValue(order.totalQuantity): orderProto.totalQuantity = decimalMaxString(order.totalQuantity)
    if isValidIntValue(order.displaySize): orderProto.displaySize = order.displaySize
    if order.orderType: orderProto.orderType = order.orderType
    if isValidFloatValue(order.lmtPrice): orderProto.lmtPrice = order.lmtPrice
    if isValidFloatValue(order.auxPrice): orderProto.auxPrice = order.auxPrice
    if order.tif: orderProto.tif = order.tif
    if order.account: orderProto.account = order.account
    if order.settlingFirm: orderProto.settlingFirm = order.settlingFirm
    if order.clearingAccount: orderProto.clearingAccount = order.clearingAccount
    if order.clearingIntent: orderProto.clearingIntent = order.clearingIntent
    if order.allOrNone: orderProto.allOrNone = order.allOrNone
    if order.blockOrder: orderProto.blockOrder = order.blockOrder
    if order.hidden: orderProto.hidden = order.hidden
    if order.outsideRth: orderProto.outsideRth = order.outsideRth
    if order.sweepToFill: orderProto.sweepToFill = order.sweepToFill
    if isValidFloatValue(order.percentOffset): orderProto.percentOffset = order.percentOffset
    if isValidFloatValue(order.trailingPercent): orderProto.trailingPercent = order.trailingPercent
    if isValidFloatValue(order.trailStopPrice): orderProto.trailStopPrice = order.trailStopPrice
    if isValidIntValue(order.minQty): orderProto.minQty = order.minQty
    if order.goodAfterTime: orderProto.goodAfterTime = order.goodAfterTime
    if order.goodTillDate: orderProto.goodTillDate = order.goodTillDate
    if order.ocaGroup: orderProto.ocaGroup = order.ocaGroup
    if order.orderRef: orderProto.orderRef = order.orderRef
    if order.rule80A: orderProto.rule80A = order.rule80A
    if isValidIntValue(order.ocaType): orderProto.ocaType = order.ocaType
    if isValidIntValue(order.triggerMethod): orderProto.triggerMethod = order.triggerMethod
    if order.activeStartTime: orderProto.activeStartTime = order.activeStartTime
    if order.activeStopTime: orderProto.activeStopTime = order.activeStopTime
    if order.faGroup: orderProto.faGroup = order.faGroup
    if order.faMethod: orderProto.faMethod = order.faMethod
    if order.faPercentage: orderProto.faPercentage = order.faPercentage
    if isValidFloatValue(order.volatility): orderProto.volatility = order.volatility
    if isValidIntValue(order.volatilityType): orderProto.volatilityType = order.volatilityType
    if order.continuousUpdate: orderProto.continuousUpdate = order.continuousUpdate
    if isValidIntValue(order.referencePriceType): orderProto.referencePriceType = order.referencePriceType
    if order.deltaNeutralOrderType: orderProto.deltaNeutralOrderType = order.deltaNeutralOrderType
    if isValidFloatValue(order.deltaNeutralAuxPrice): orderProto.deltaNeutralAuxPrice = order.deltaNeutralAuxPrice
    if isValidIntValue(order.deltaNeutralConId): orderProto.deltaNeutralConId = order.deltaNeutralConId
    if order.deltaNeutralOpenClose: orderProto.deltaNeutralOpenClose = order.deltaNeutralOpenClose
    if order.deltaNeutralShortSale: orderProto.deltaNeutralShortSale = order.deltaNeutralShortSale
    if isValidIntValue(order.deltaNeutralShortSaleSlot): orderProto.deltaNeutralShortSaleSlot = order.deltaNeutralShortSaleSlot
    if order.deltaNeutralDesignatedLocation: orderProto.deltaNeutralDesignatedLocation = order.deltaNeutralDesignatedLocation
    if isValidIntValue(order.scaleInitLevelSize): orderProto.scaleInitLevelSize = order.scaleInitLevelSize
    if isValidIntValue(order.scaleSubsLevelSize): orderProto.scaleSubsLevelSize = order.scaleSubsLevelSize
    if isValidFloatValue(order.scalePriceIncrement): orderProto.scalePriceIncrement = order.scalePriceIncrement
    if isValidFloatValue(order.scalePriceAdjustValue): orderProto.scalePriceAdjustValue = order.scalePriceAdjustValue
    if isValidIntValue(order.scalePriceAdjustInterval): orderProto.scalePriceAdjustInterval = order.scalePriceAdjustInterval
    if isValidFloatValue(order.scaleProfitOffset): orderProto.scaleProfitOffset = order.scaleProfitOffset
    if order.scaleAutoReset: orderProto.scaleAutoReset = order.scaleAutoReset
    if isValidIntValue(order.scaleInitPosition): orderProto.scaleInitPosition = order.scaleInitPosition
    if isValidIntValue(order.scaleInitFillQty): orderProto.scaleInitFillQty = order.scaleInitFillQty
    if order.scaleRandomPercent: orderProto.scaleRandomPercent = order.scaleRandomPercent
    if order.scaleTable: orderProto.scaleTable = order.scaleTable
    if order.hedgeType: orderProto.hedgeType = order.hedgeType
    if order.hedgeParam: orderProto.hedgeParam = order.hedgeParam

    if order.algoStrategy: orderProto.algoStrategy = order.algoStrategy
    fillTagValueList(order.algoParams, orderProto.algoParams)
    if order.algoId: orderProto.algoId = order.algoId

    fillTagValueList(order.smartComboRoutingParams, orderProto.smartComboRoutingParams)

    if order.whatIf: orderProto.whatIf = order.whatIf
    if order.transmit: orderProto.transmit = order.transmit
    if order.overridePercentageConstraints: orderProto.overridePercentageConstraints = order.overridePercentageConstraints
    if order.openClose: orderProto.openClose = order.openClose
    if isValidIntValue(order.origin): orderProto.origin = order.origin
    if isValidIntValue(order.shortSaleSlot): orderProto.shortSaleSlot = order.shortSaleSlot
    if order.designatedLocation: orderProto.designatedLocation = order.designatedLocation
    if isValidIntValue(order.exemptCode): orderProto.exemptCode = order.exemptCode
    if order.deltaNeutralSettlingFirm: orderProto.deltaNeutralSettlingFirm = order.deltaNeutralSettlingFirm
    if order.deltaNeutralClearingAccount: orderProto.deltaNeutralClearingAccount = order.deltaNeutralClearingAccount
    if order.deltaNeutralClearingIntent: orderProto.deltaNeutralClearingIntent = order.deltaNeutralClearingIntent
    if isValidIntValue(order.discretionaryAmt): orderProto.discretionaryAmt = order.discretionaryAmt
    if order.optOutSmartRouting: orderProto.optOutSmartRouting = order.optOutSmartRouting
    if isValidIntValue(order.exemptCode): orderProto.exemptCode = order.exemptCode
    if isValidFloatValue(order.startingPrice): orderProto.startingPrice = order.startingPrice
    if isValidFloatValue(order.stockRefPrice): orderProto.stockRefPrice = order.stockRefPrice
    if isValidFloatValue(order.delta): orderProto.delta = order.delta
    if isValidFloatValue(order.stockRangeLower): orderProto.stockRangeLower = order.stockRangeLower
    if isValidFloatValue(order.stockRangeUpper): orderProto.stockRangeUpper = order.stockRangeUpper
    if order.notHeld: orderProto.notHeld = order.notHeld

    fillTagValueList(order.orderMiscOptions, orderProto.orderMiscOptions)

    if order.solicited: orderProto.solicited = order.solicited
    if order.randomizeSize: orderProto.randomizeSize = order.randomizeSize
    if order.randomizePrice: orderProto.randomizePrice = order.randomizePrice
    if isValidIntValue(order.referenceContractId): orderProto.referenceContractId = order.referenceContractId
    if isValidFloatValue(order.peggedChangeAmount): orderProto.peggedChangeAmount = order.peggedChangeAmount
    if order.isPeggedChangeAmountDecrease: orderProto.isPeggedChangeAmountDecrease = order.isPeggedChangeAmountDecrease
    if isValidFloatValue(order.referenceChangeAmount): orderProto.referenceChangeAmount = order.referenceChangeAmount
    if order.referenceExchangeId: orderProto.referenceExchangeId = order.referenceExchangeId
    if order.adjustedOrderType: orderProto.adjustedOrderType = order.adjustedOrderType
    if isValidFloatValue(order.triggerPrice): orderProto.triggerPrice = order.triggerPrice
    if isValidFloatValue(order.adjustedStopPrice): orderProto.adjustedStopPrice = order.adjustedStopPrice
    if isValidFloatValue(order.adjustedStopLimitPrice): orderProto.adjustedStopLimitPrice = order.adjustedStopLimitPrice
    if isValidFloatValue(order.adjustedTrailingAmount): orderProto.adjustedTrailingAmount = order.adjustedTrailingAmount
    if isValidIntValue(order.adjustableTrailingUnit): orderProto.adjustableTrailingUnit = order.adjustableTrailingUnit
    if isValidFloatValue(order.lmtPriceOffset): orderProto.lmtPriceOffset = order.lmtPriceOffset

    orderConditionList = createConditionsProto(order)
    if orderConditionList is not None and orderConditionList: orderProto.conditions.extend(orderConditionList)
    if order.conditionsCancelOrder: orderProto.conditionsCancelOrder = order.conditionsCancelOrder
    if order.conditionsIgnoreRth: orderProto.conditionsIgnoreRth = order.conditionsIgnoreRth

    if order.modelCode: orderProto.modelCode = order.modelCode
    if order.extOperator: orderProto.extOperator = order.extOperator

    softDollarTier = createSoftDollarTierProto(order)
    if softDollarTier is not None: orderProto.softDollarTier.CopyFrom(softDollarTier)

    if isValidFloatValue(order.cashQty): orderProto.cashQty = order.cashQty
    if order.mifid2DecisionMaker: orderProto.mifid2DecisionMaker = order.mifid2DecisionMaker
    if order.mifid2DecisionAlgo: orderProto.mifid2DecisionAlgo = order.mifid2DecisionAlgo
    if order.mifid2ExecutionTrader: orderProto.mifid2ExecutionTrader = order.mifid2ExecutionTrader
    if order.mifid2ExecutionAlgo: orderProto.mifid2ExecutionAlgo = order.mifid2ExecutionAlgo
    if order.dontUseAutoPriceForHedge: orderProto.dontUseAutoPriceForHedge = order.dontUseAutoPriceForHedge
    if order.isOmsContainer: orderProto.isOmsContainer = order.isOmsContainer
    if order.discretionaryUpToLimitPrice: orderProto.discretionaryUpToLimitPrice = order.discretionaryUpToLimitPrice
    if order.usePriceMgmtAlgo is not None: orderProto.usePriceMgmtAlgo = 1 if order.usePriceMgmtAlgo else 0
    if isValidIntValue(order.duration): orderProto.duration = order.duration
    if isValidIntValue(order.postToAts): orderProto.postToAts = order.postToAts
    if order.advancedErrorOverride: orderProto.advancedErrorOverride = order.advancedErrorOverride
    if order.manualOrderTime: orderProto.manualOrderTime = order.manualOrderTime
    if isValidIntValue(order.minTradeQty): orderProto.minTradeQty = order.minTradeQty
    if isValidIntValue(order.minCompeteSize): orderProto.minCompeteSize = order.minCompeteSize
    if isValidFloatValue(order.competeAgainstBestOffset): orderProto.competeAgainstBestOffset = order.competeAgainstBestOffset
    if isValidFloatValue(order.midOffsetAtWhole): orderProto.midOffsetAtWhole = order.midOffsetAtWhole
    if isValidFloatValue(order.midOffsetAtHalf): orderProto.midOffsetAtHalf = order.midOffsetAtHalf
    if order.customerAccount: orderProto.customerAccount = order.customerAccount
    if order.professionalCustomer: orderProto.professionalCustomer = order.professionalCustomer
    if order.bondAccruedInterest: orderProto.bondAccruedInterest = order.bondAccruedInterest
    if order.includeOvernight: orderProto.includeOvernight = order.includeOvernight
    if isValidIntValue(order.manualOrderIndicator): orderProto.manualOrderIndicator = order.manualOrderIndicator
    if order.submitter: orderProto.submitter = order.submitter
    if order.autoCancelParent: orderProto.autoCancelParent = order.autoCancelParent
    if order.imbalanceOnly: orderProto.imbalanceOnly = order.imbalanceOnly

    return orderProto

def createConditionsProto(order: Order) -> list[OrderConditionProto]:
    orderConditionProtoList = []
    try:
        if order.conditions is not None and order.conditions:
            for orderCondition in order.conditions:
                conditionType = orderCondition.condType

                if OrderCondition.Price == conditionType:
                    orderConditionProto = createPriceConditionProto(orderCondition)
                elif OrderCondition.Time == conditionType:
                    orderConditionProto = createTimeConditionProto(orderCondition)
                elif OrderCondition.Margin == conditionType:
                    orderConditionProto = createMarginConditionProto(orderCondition)
                elif OrderCondition.Execution == conditionType:
                    orderConditionProto = createExecutionConditionProto(orderCondition)
                elif OrderCondition.Volume == conditionType:
                    orderConditionProto = createVolumeConditionProto(orderCondition)
                elif OrderCondition.PercentChange == conditionType:
                    orderConditionProto = createPercentChangeConditionProto(orderCondition)

                if orderConditionProto is not None: orderConditionProtoList.append(orderConditionProto)

    except Exception:
        raise ClientException(ERROR_ENCODING_PROTOBUF.code(), ERROR_ENCODING_PROTOBUF.msg(), "Error encoding conditions")

    return orderConditionProtoList

@staticmethod
def createOrderConditionProto(orderCondition: OrderCondition) -> OrderConditionProto:
    conditionType = orderCondition.condType
    isConjunctionConnection = orderCondition.isConjunctionConnection
    orderConditionProto = OrderConditionProto()
    if isValidIntValue(conditionType): orderConditionProto.type = conditionType
    orderConditionProto.isConjunctionConnection = isConjunctionConnection
    return orderConditionProto

@staticmethod
def createOperatorConditionProto(operatorCondition: OperatorCondition) -> OrderConditionProto:
    orderConditionProto = createOrderConditionProto(operatorCondition)
    operatorConditionProto = OrderConditionProto()
    operatorConditionProto.MergeFrom(orderConditionProto)
    operatorConditionProto.isMore = operatorCondition.isMore
    return operatorConditionProto

@staticmethod
def createContractConditionProto(contractCondition: ContractCondition) -> OrderConditionProto:
    operatorConditionProto = createOperatorConditionProto(contractCondition)
    contractConditionProto = OrderConditionProto()
    contractConditionProto.MergeFrom(operatorConditionProto)
    if isValidIntValue(contractCondition.conId): contractConditionProto.conId = contractCondition.conId
    if contractCondition.exchange: contractConditionProto.exchange = contractCondition.exchange
    return contractConditionProto

@staticmethod
def createPriceConditionProto(priceCondition: PriceCondition) -> OrderConditionProto:
    contractConditionProto = createContractConditionProto(priceCondition)
    priceConditionProto = OrderConditionProto()
    priceConditionProto.MergeFrom(contractConditionProto)
    if isValidFloatValue(priceCondition.price): priceConditionProto.price = priceCondition.price
    if isValidIntValue(priceCondition.triggerMethod): priceConditionProto.triggerMethod = priceCondition.triggerMethod
    return priceConditionProto

@staticmethod
def createTimeConditionProto(timeCondition: TimeCondition) -> OrderConditionProto:
    operatorConditionProto = createOperatorConditionProto(timeCondition)
    timeConditionProto = OrderConditionProto()
    timeConditionProto.MergeFrom(operatorConditionProto)
    if timeCondition.time: timeConditionProto.time = timeCondition.time
    return timeConditionProto

@staticmethod
def createMarginConditionProto(marginCondition: MarginCondition) -> OrderConditionProto:
    operatorConditionProto = createOperatorConditionProto(marginCondition)
    marginConditionProto = OrderConditionProto()
    marginConditionProto.MergeFrom(operatorConditionProto)
    if isValidFloatValue(marginCondition.percent): marginConditionProto.percent = marginCondition.percent
    return marginConditionProto

@staticmethod
def createExecutionConditionProto(executionCondition: ExecutionCondition) -> OrderConditionProto:
    orderConditionProto = createOrderConditionProto(executionCondition)
    executionConditionProto = OrderConditionProto()
    executionConditionProto.MergeFrom(orderConditionProto)
    if executionCondition.secType: executionConditionProto.secType = executionCondition.secType
    if executionCondition.exchange: executionConditionProto.exchange = executionCondition.exchange
    if executionCondition.symbol: executionConditionProto.symbol = executionCondition.symbol
    return executionConditionProto

@staticmethod
def createVolumeConditionProto(volumeCondition: VolumeCondition) -> OrderConditionProto:
    contractConditionProto = createContractConditionProto(volumeCondition)
    volumeConditionProto = OrderConditionProto()
    volumeConditionProto.MergeFrom(contractConditionProto)
    if isValidIntValue(volumeCondition.volume): volumeConditionProto.volume = volumeCondition.volume
    return volumeConditionProto

@staticmethod
def createPercentChangeConditionProto(percentChangeCondition: PercentChangeCondition) -> OrderConditionProto:
    contractConditionProto = createContractConditionProto(percentChangeCondition)
    percentChangeConditionProto = OrderConditionProto()
    percentChangeConditionProto.MergeFrom(contractConditionProto)
    if isValidFloatValue(percentChangeCondition.changePercent): percentChangeConditionProto.changePercent = percentChangeCondition.changePercent
    return percentChangeConditionProto

@staticmethod
def createSoftDollarTierProto(order: Order) -> SoftDollarTierProto:
    softDollarTierProto = None
    tier = order.softDollarTier
    if tier is not None:
        softDollarTierProto = SoftDollarTierProto()
        if tier.name: softDollarTierProto.name = tier.name
        if tier.val: softDollarTierProto.value = tier.val
        if tier.displayName: softDollarTierProto.displayName = tier.displayName
    return softDollarTierProto

@staticmethod
def fillTagValueList(tagValueList: list, orderProtoMap: dict):
    if tagValueList is not None and tagValueList:
        for tagValue in tagValueList: 
            orderProtoMap[tagValue.tag] = tagValue.value

@staticmethod
def createCancelOrderRequestProto(orderId: int, orderCancel: OrderCancel) -> CancelOrderRequestProto:
    cancelOrderRequestProto = CancelOrderRequestProto()
    if isValidIntValue(orderId): cancelOrderRequestProto.orderId = orderId
    orderCancelProto = createOrderCancelProto(orderCancel)
    if orderCancelProto is not None: cancelOrderRequestProto.orderCancel.CopyFrom(orderCancelProto)
    return cancelOrderRequestProto

@staticmethod
def createGlobalCancelRequestProto(orderCancel: OrderCancel) -> GlobalCancelRequestProto:
    globalCancelRequestProto = GlobalCancelRequestProto()
    orderCancelProto = createOrderCancelProto(orderCancel)
    if orderCancelProto is not None: globalCancelRequestProto.orderCancel.CopyFrom(orderCancelProto)
    return globalCancelRequestProto

@staticmethod
def createOrderCancelProto(orderCancel: OrderCancel) -> OrderCancelProto:
    if orderCancel is None:
        return None
    orderCancelProto = OrderCancelProto()
    if orderCancel.manualOrderCancelTime: orderCancelProto.manualOrderCancelTime = orderCancel.manualOrderCancelTime
    if orderCancel.extOperator: orderCancelProto.extOperator = orderCancel.extOperator
    if isValidIntValue(orderCancel.manualOrderIndicator): orderCancelProto.manualOrderIndicator = orderCancel.manualOrderIndicator
    return orderCancelProto

@staticmethod
def createAllOpenOrdersRequestProto() -> AllOpenOrdersRequestProto:
    allOpenOrdersRequestProto = AllOpenOrdersRequestProto()
    return allOpenOrdersRequestProto

@staticmethod
def createAutoOpenOrdersRequestProto(autoBind: bool) -> AutoOpenOrdersRequestProto:
    autoOpenOrdersRequestProto = AutoOpenOrdersRequestProto()
    if autoBind: autoOpenOrdersRequestProto.autoBind = autoBind
    return autoOpenOrdersRequestProto

@staticmethod
def createOpenOrdersRequestProto() -> OpenOrdersRequestProto:
    openOrdersRequestProto = OpenOrdersRequestProto()
    return openOrdersRequestProto

@staticmethod
def createCompletedOrdersRequestProto(apiOnly: bool) -> CompletedOrdersRequestProto:
    completedOrdersRequestProto = CompletedOrdersRequestProto()
    if apiOnly: completedOrdersRequestProto.apiOnly = apiOnly
    return completedOrdersRequestProto

@staticmethod
def createContractDataRequestProto(reqId: int, contract: Contract) -> ContractDataRequestProto:
    contractDataRequestProto = ContractDataRequestProto()
    if isValidIntValue(reqId): contractDataRequestProto.reqId = reqId
    contractProto = createContractProto(contract, None)
    if contractProto is not None: contractDataRequestProto.contract.CopyFrom(contractProto)
    return contractDataRequestProto

@staticmethod
def createMarketDataRequestProto(reqId: int, contract: Contract, genericTickList: str, snapshot: bool, regulatorySnapshot: bool, marketDataOptionsList: TagValueList) -> MarketDataRequestProto:
    marketDataRequestProto = MarketDataRequestProto()
    if isValidIntValue(reqId): marketDataRequestProto.reqId = reqId
    contractProto = createContractProto(contract, None)
    if contractProto is not None: marketDataRequestProto.contract.CopyFrom(contractProto)
    if genericTickList: marketDataRequestProto.genericTickList = genericTickList
    if snapshot: marketDataRequestProto.snapshot = snapshot
    if regulatorySnapshot: marketDataRequestProto.regulatorySnapshot = regulatorySnapshot
    fillTagValueList(marketDataOptionsList, marketDataRequestProto.marketDataOptions)
    return marketDataRequestProto

@staticmethod
def createMarketDepthRequestProto(reqId: int, contract: Contract, numRows: int, isSmartDepth: bool, marketDepthOptionsList: TagValueList) -> MarketDepthRequestProto:
    marketDepthRequestProto = MarketDepthRequestProto()
    if isValidIntValue(reqId): marketDepthRequestProto.reqId = reqId
    contractProto = createContractProto(contract, None)
    if contractProto is not None: marketDepthRequestProto.contract.CopyFrom(contractProto)
    if isValidIntValue(numRows): marketDepthRequestProto.numRows = numRows
    if isSmartDepth: marketDepthRequestProto.isSmartDepth = isSmartDepth
    fillTagValueList(marketDepthOptionsList, marketDepthRequestProto.marketDepthOptions)
    return marketDepthRequestProto

@staticmethod
def createMarketDataTypeRequestProto(marketDataType: int) -> MarketDataTypeRequestProto:
    marketDataTypeRequestProto = MarketDataTypeRequestProto()
    if isValidIntValue(marketDataType): marketDataTypeRequestProto.marketDataType = marketDataType
    return marketDataTypeRequestProto

@staticmethod
def createCancelMarketDataProto(reqId: int) -> CancelMarketDataProto:
    cancelMarketDataProto = CancelMarketDataProto()
    if isValidIntValue(reqId): cancelMarketDataProto.reqId = reqId
    return cancelMarketDataProto

@staticmethod
def createCancelMarketDepthProto(reqId: int, isSmartDepth: bool) -> CancelMarketDepthProto:
    cancelMarketDepthProto = CancelMarketDepthProto()
    if isValidIntValue(reqId): cancelMarketDepthProto.reqId = reqId
    if isSmartDepth: cancelMarketDepthProto.isSmartDepth = isSmartDepth
    return cancelMarketDepthProto

@staticmethod
def createAccountDataRequestProto(subscribe: bool, acctCode: str) -> AccountDataRequestProto:
    accountDataRequestProto = AccountDataRequestProto()
    if subscribe: accountDataRequestProto.subscribe = subscribe
    if acctCode: accountDataRequestProto.acctCode = acctCode
    return accountDataRequestProto

@staticmethod
def createManagedAccountsRequestProto() -> ManagedAccountsRequestProto:
    managedAccountsRequestProto = ManagedAccountsRequestProto()
    return managedAccountsRequestProto

@staticmethod
def createPositionsRequestProto() -> PositionsRequestProto:
    positionsRequestProto = PositionsRequestProto()
    return positionsRequestProto

@staticmethod
def createCancelPositionsRequestProto() -> CancelPositionsProto:
    cancelPositionsProto = CancelPositionsProto()
    return cancelPositionsProto

@staticmethod
def createAccountSummaryRequestProto(reqId: int, group: str, tags: str) -> AccountSummaryRequestProto:
    accountSummaryRequestProto = AccountSummaryRequestProto()
    if isValidIntValue(reqId): accountSummaryRequestProto.reqId = reqId
    if group: accountSummaryRequestProto.group = group
    if tags: accountSummaryRequestProto.tags = tags
    return accountSummaryRequestProto

@staticmethod
def createCancelAccountSummaryRequestProto(reqId: int) -> CancelAccountSummaryProto:
    cancelAccountSummaryProto = CancelAccountSummaryProto()
    if isValidIntValue(reqId): cancelAccountSummaryProto.reqId = reqId
    return cancelAccountSummaryProto

@staticmethod
def createPositionsMultiRequestProto(reqId: int, account: str, modelCode: str) -> PositionsMultiRequestProto:
    positionsMultiRequestProto = PositionsMultiRequestProto()
    if isValidIntValue(reqId): positionsMultiRequestProto.reqId = reqId
    if account: positionsMultiRequestProto.account = account
    if modelCode: positionsMultiRequestProto.modelCode = modelCode
    return positionsMultiRequestProto

@staticmethod
def createCancelPositionsMultiRequestProto(reqId: int) -> CancelPositionsMultiProto:
    cancelPositionsMultiProto = CancelPositionsMultiProto()
    if isValidIntValue(reqId): cancelPositionsMultiProto.reqId = reqId
    return cancelPositionsMultiProto

@staticmethod
def createAccountUpdatesMultiRequestProto(reqId: int, account: str, modelCode: str, ledgerAndNLV: bool) -> AccountUpdatesMultiRequestProto:
    accountUpdatesMultiRequestProto = AccountUpdatesMultiRequestProto()
    if isValidIntValue(reqId): accountUpdatesMultiRequestProto.reqId = reqId
    if account: accountUpdatesMultiRequestProto.account = account
    if modelCode: accountUpdatesMultiRequestProto.modelCode = modelCode
    if ledgerAndNLV: accountUpdatesMultiRequestProto.ledgerAndNLV = ledgerAndNLV
    return accountUpdatesMultiRequestProto

@staticmethod
def createCancelAccountUpdatesMultiRequestProto(reqId: int) -> CancelAccountUpdatesMultiProto:
    cancelAccountUpdatesMultiProto = CancelAccountUpdatesMultiProto()
    if isValidIntValue(reqId): cancelAccountUpdatesMultiProto.reqId = reqId
    return cancelAccountUpdatesMultiProto

@staticmethod
def createHistoricalDataRequestProto(reqId: int, contract: Contract, endDateTime: str, duration: str, barSizeSetting: str, whatToShow: str, useRTH: bool, formatDate: int,
                                    keepUpToDate: bool, chartOptionsList: TagValueList) -> HistoricalDataRequestProto:
    historicalDataRequestProto = HistoricalDataRequestProto()
    if isValidIntValue(reqId): historicalDataRequestProto.reqId = reqId
    contractProto = createContractProto(contract, None)
    if contractProto is not None: historicalDataRequestProto.contract.CopyFrom(contractProto)
    if endDateTime: historicalDataRequestProto.endDateTime = endDateTime
    if duration: historicalDataRequestProto.duration = duration
    if barSizeSetting: historicalDataRequestProto.barSizeSetting = barSizeSetting
    if whatToShow: historicalDataRequestProto.whatToShow = whatToShow
    if useRTH: historicalDataRequestProto.useRTH = useRTH
    if isValidIntValue(formatDate): historicalDataRequestProto.formatDate = formatDate
    if keepUpToDate: historicalDataRequestProto.keepUpToDate = keepUpToDate
    fillTagValueList(chartOptionsList, historicalDataRequestProto.chartOptions)
    return historicalDataRequestProto

@staticmethod
def createRealTimeBarsRequestProto(reqId: int, contract: Contract, barSize: int, whatToShow: str, useRTH: bool, realTimeBarsOptionsList: TagValueList) -> RealTimeBarsRequestProto:
    realTimeBarsRequestProto = RealTimeBarsRequestProto()
    if isValidIntValue(reqId): realTimeBarsRequestProto.reqId = reqId
    contractProto = createContractProto(contract, None)
    if contractProto is not None: realTimeBarsRequestProto.contract.CopyFrom(contractProto)
    if isValidIntValue(barSize): realTimeBarsRequestProto.barSize = barSize
    if whatToShow: realTimeBarsRequestProto.whatToShow = whatToShow
    if useRTH: realTimeBarsRequestProto.useRTH = useRTH
    fillTagValueList(realTimeBarsOptionsList, realTimeBarsRequestProto.realTimeBarsOptions)
    return realTimeBarsRequestProto

@staticmethod
def createHeadTimestampRequestProto(reqId: int, contract: Contract, whatToShow: str, useRTH: bool, formatDate: int) -> HeadTimestampRequestProto:
    headTimestampRequestProto = HeadTimestampRequestProto()
    if isValidIntValue(reqId): headTimestampRequestProto.reqId = reqId
    contractProto = createContractProto(contract, None)
    if contractProto is not None: headTimestampRequestProto.contract.CopyFrom(contractProto)
    if whatToShow: headTimestampRequestProto.whatToShow = whatToShow
    if useRTH: headTimestampRequestProto.useRTH = useRTH
    if isValidIntValue(formatDate): headTimestampRequestProto.formatDate = formatDate
    return headTimestampRequestProto

@staticmethod
def createHistogramDataRequestProto(reqId: int, contract: Contract, useRTH: bool, timePeriod: str) -> HistogramDataRequestProto:
    histogramDataRequestProto = HistogramDataRequestProto()
    if isValidIntValue(reqId): histogramDataRequestProto.reqId = reqId
    contractProto = createContractProto(contract, None)
    if contractProto is not None: histogramDataRequestProto.contract.CopyFrom(contractProto)
    if useRTH: histogramDataRequestProto.useRTH = useRTH
    if timePeriod: histogramDataRequestProto.timePeriod = timePeriod
    return histogramDataRequestProto

@staticmethod
def createHistoricalTicksRequestProto(reqId: int, contract: Contract, startDateTime: str, endDateTime: str, numberOfTicks: int, whatToShow: str, useRTH: bool, ignoreSize: bool,
                                     miscOptionsList: TagValueList) -> HistoricalTicksRequestProto:
    historicalTicksRequestProto = HistoricalTicksRequestProto()
    if isValidIntValue(reqId): historicalTicksRequestProto.reqId = reqId
    contractProto = createContractProto(contract, None)
    if contractProto is not None: historicalTicksRequestProto.contract.CopyFrom(contractProto)
    if startDateTime: historicalTicksRequestProto.startDateTime = startDateTime
    if endDateTime: historicalTicksRequestProto.endDateTime = endDateTime
    if isValidIntValue(numberOfTicks): historicalTicksRequestProto.numberOfTicks = numberOfTicks
    if whatToShow: historicalTicksRequestProto.whatToShow = whatToShow
    if useRTH: historicalTicksRequestProto.useRTH = useRTH
    if ignoreSize: historicalTicksRequestProto.ignoreSize = ignoreSize
    fillTagValueList(miscOptionsList, historicalTicksRequestProto.miscOptions)
    return historicalTicksRequestProto

@staticmethod
def createTickByTickRequestProto(reqId: int, contract: Contract, tickType: str, numberOfTicks: int, ignoreSize: bool) -> TickByTickRequestProto:
    tickByTickRequestProto = TickByTickRequestProto()
    if isValidIntValue(reqId): tickByTickRequestProto.reqId = reqId
    contractProto = createContractProto(contract, None)
    if contractProto is not None: tickByTickRequestProto.contract.CopyFrom(contractProto)
    if tickType: tickByTickRequestProto.tickType = tickType
    if isValidIntValue(numberOfTicks): tickByTickRequestProto.numberOfTicks = numberOfTicks
    if ignoreSize: tickByTickRequestProto.ignoreSize = ignoreSize
    return tickByTickRequestProto

@staticmethod
def createCancelHistoricalDataProto(reqId: int) -> CancelHistoricalDataProto:
    cancelHistoricalDataProto = CancelHistoricalDataProto()
    if isValidIntValue(reqId): cancelHistoricalDataProto.reqId = reqId
    return cancelHistoricalDataProto

@staticmethod
def createCancelRealTimeBarsProto(reqId: int) -> CancelRealTimeBarsProto:
    cancelRealTimeBarsProto = CancelRealTimeBarsProto()
    if isValidIntValue(reqId): cancelRealTimeBarsProto.reqId = reqId
    return cancelRealTimeBarsProto

@staticmethod
def createCancelHeadTimestampProto(reqId: int) -> CancelHeadTimestampProto:
    cancelHeadTimestampProto = CancelHeadTimestampProto()
    if isValidIntValue(reqId): cancelHeadTimestampProto.reqId = reqId
    return cancelHeadTimestampProto

@staticmethod
def createCancelHistogramDataProto(reqId: int) -> CancelHistogramDataProto:
    cancelHistogramDataProto = CancelHistogramDataProto()
    if isValidIntValue(reqId): cancelHistogramDataProto.reqId = reqId
    return cancelHistogramDataProto

@staticmethod
def createCancelTickByTickProto(reqId: int) -> CancelTickByTickProto:
    cancelTickByTickProto = CancelTickByTickProto()
    if isValidIntValue(reqId): cancelTickByTickProto.reqId = reqId
    return cancelTickByTickProto
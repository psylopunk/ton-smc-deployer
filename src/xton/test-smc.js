const ContractExecutor = require('ton-contract-executor');
const SmartContract = ContractExecutor.SmartContract;
const TonLib = require('ton');
const Cell = TonLib.Cell;
const fs = require('fs');
const exec = require('child_process').exec;

async function main() {
  let contract = await SmartContract.fromCell(
    Cell.fromBoc(process.argv[2])[0],
    Cell.fromBoc('b5ee9c724101010100020000004cacb9cd')[0]
  );
  contract.config.debug = true;
  let contractAddress = TonLib.contractAddress({
    workchain: 0,
    initialCode: contract.codeCell,
    initialData: contract.codeData
  })

  let from = TonLib.Address.parseFriendly('EQBpCx6-VflnZormL6afG_Cm3bP1Xe3uQg4vF03fZZRrRuIO').address;
  let res = await contract.sendInternalMessage(new TonLib.InternalMessage({
      to: contractAddress,
      from: from,
      value: TonLib.toNano(11),
      bounce: false,
      body: new TonLib.CommonMessageInfo({
          body: new TonLib.CellMessage(new Cell())
      })
  }))
  let logs = res.logs.split('\n');
  for (i in logs) {
    logs[i] = logs[i].split('\n');
    for (y in logs[i]) {
      console.log(
          (logs[i][y].indexOf('#DEBUG#') !== -1 ? '\x1b[47m\x1b[30m' : '') + logs[i][y] + '\x1b[40m\x1b[37m'
      );
    }
  }
  return 0;
}

main().then(() => {})

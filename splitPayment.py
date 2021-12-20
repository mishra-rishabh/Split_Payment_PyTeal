"""
  reference: https://pyteal.readthedocs.io/en/stable/examples.html
"""
from pyteal import *
from decouple import config

# fee and addresses
tmpl_fee = Int( 1000 )
tmpl_receiver1 = Addr( config( "RECEIVER1_ADDR" ) )
tmpl_receiver2 = Addr( config( "RECEIVER2_ADDR" ) )
tmpl_owner = Addr( config( "OWNER_ADDR" ) )

# ratios (numerator and denominator)
tmpl_ratio_numerator = Int( 1 )
tmpl_ratio_denominator = Int( 3 )

tmpl_minimum_pay = Int( 1000 )
tmpl_timeout = Int( 3000 )

def splitPayment(
  tmpl_fee = tmpl_fee , tmpl_owner = tmpl_owner ,
  tmpl_receiver1 = tmpl_receiver1 , tmpl_receiver2 = tmpl_receiver2 ,
  tmpl_ratio_numerator = tmpl_ratio_numerator , tmpl_ratio_denominator = tmpl_ratio_denominator ,
  tmpl_minimum_pay = tmpl_minimum_pay , tmpl_timeout = tmpl_timeout
):
  split_core = And(
    Txn.type_enum() == TxnType.Payment ,
    # or
    # Txn.type_enum() == Int( 1 ) ,
    Txn.fee() < tmpl_fee ,
    Txn.rekey_to() == Global.zero_address()
  )

  split_transfer = And(
    Gtxn[ 0 ].sender() == Gtxn[ 1 ].sender() ,
    Txn.close_remainder_to() == Global.zero_address() ,
    Gtxn[ 0 ].receiver() == tmpl_receiver1 ,
    Gtxn[ 1 ].receiver() == tmpl_receiver2 ,
    Gtxn[ 0 ].amount() == ( ( Gtxn[ 0 ].amount() + Gtxn[ 1 ].amount() ) * tmpl_ratio_numerator ) / tmpl_ratio_denominator
  )

  split_close = And(
    Txn.close_remainder_to() == tmpl_owner ,
    Txn.receiver() == Global.zero_address() ,
    Txn.amount() == Int( 0 ) ,
    Txn.first_valid() > tmpl_timeout
  )

  split_program = And(
    split_core ,
    If(
      Global.group_size() == Int( 2 ) ,
      split_transfer , split_close
    )
  )

  return split_program

if __name__ == "__main__":
  with open( "tealCode/splitPayment.teal" , "w" ) as f:
    compiled = compileTeal( splitPayment() , Mode.Signature , version = 5 )
    f.write( compiled )
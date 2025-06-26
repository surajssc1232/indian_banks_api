import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphene.relay.node import Node
from .models import Bank, Branch

class BankObject(SQLAlchemyObjectType):
    class Meta:
        model = Bank
        interfaces = (Node, )

class BranchObject(SQLAlchemyObjectType):
    class Meta:
        model = Branch
        interfaces = (Node, )

class Query(graphene.ObjectType):
    node = Node.Field()
    
    branches = SQLAlchemyConnectionField(BranchObject)
    
    banks = SQLAlchemyConnectionField(BankObject)
    
    branch_by_ifsc = graphene.Field(BranchObject, ifsc=graphene.String(required=True))
    
    branches_by_bank = graphene.List(BranchObject, bank_name=graphene.String(required=True))
    
    branches_by_city = graphene.List(BranchObject, city=graphene.String(required=True))
    
    branches_by_state = graphene.List(BranchObject, state=graphene.String(required=True))
    
    def resolve_branch_by_ifsc(self, info, ifsc):
        return Branch.query.filter_by(ifsc=ifsc).first()
    
    def resolve_branches_by_bank(self, info, bank_name):
        return Branch.query.join(Bank).filter(Bank.name.ilike(f'%{bank_name}%')).all()
    
    def resolve_branches_by_city(self, info, city):
        return Branch.query.filter(Branch.city.ilike(f'%{city}%')).all()
    
    def resolve_branches_by_state(self, info, state):
        return Branch.query.filter(Branch.state.ilike(f'%{state}%')).all()

schema = graphene.Schema(query=Query)

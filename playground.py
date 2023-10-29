""" Playground file to just write some code to test some stuff out.  """
from sqlalchemy import ForeignKey, create_engine, Table, Column, Integer, String, MetaData, select, join, alias

# engine = create_engine("sqlite:///example.db", echo=True)
metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("fullname", String),
)

addresses = Table(
    "addresses",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", None, ForeignKey("users.id")),
    Column("email_address", String, nullable=False),
)

statement = addresses

# Define an alias for the users table
users_alias = alias(users, "address_user")


# Build a join between the users table and the addresses table using the alias
join_condition = users_alias.c.id == addresses.c.user_id
join = join(users_alias, statement, join_condition)

# Select columns from both tables using the alias
stmt = select(users_alias.columns.name.label("user name"), addresses.c.email_address).select_from(join)

print(str(stmt))
# Execute the statement
# with engine.connect() as conn:
#     result = conn.execute(stmt).fetchall()

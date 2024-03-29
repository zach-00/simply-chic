from .pool import pool
from pydantic import BaseModel
from typing import List, Union
from fastapi import HTTPException


class AccountOut(BaseModel):
    id: int
    username: str
    full_name: str
    phone_number: str
    disabled: bool

class AccountOutWithPass(AccountOut):
    hashed_password: str

class AccountsOut(BaseModel):
    accounts: list[AccountOut]

class AccountIn(BaseModel):
    username: str
    full_name: str
    phone_number: str
    password: str
    disabled: bool

class AccountRepo:
    def get_accounts_verify(self):
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        SELECT * FROM accounts;
                        """
                    )
                    accounts = result.fetchall()
                    accounts_list = []

                    for acc in accounts:
                        account = AccountOutWithPass(
                            id=acc[0],
                            username=acc[1],
                            full_name=acc[2],
                            phone_number=acc[3],
                            hashed_password=acc[4],
                            disabled=acc[5],
                        )
                        accounts_list.append(account)
                    return accounts_list

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e),
            )


    def get_accounts(self):
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        SELECT
                            id,
                            username,
                            full_name,
                            phone_number,
                            disabled
                        FROM accounts;
                        """
                    )
                    accounts = result.fetchall()
                    accounts_list = []
                    for acc in accounts:
                        account = AccountOut(
                            id=acc[0],
                            username=acc[1],
                            full_name=acc[2],
                            phone_number=acc[3],
                            disabled=acc[4],
                        )
                        accounts_list.append(account)
                    return accounts_list

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e),
            )


    def create_account(self, account: AccountIn, hashed_pw: str):
        try:
            with pool.connection() as conn:
                with conn.cursor() as db:
                    result = db.execute(
                        """
                        INSERT INTO accounts (username, full_name, phone_number, hashed_password, disabled)
                        VALUES
                            (%s, %s, %s, %s, %s)
                        RETURNING
                        id,
                        username,
                        full_name,
                        phone_number,
                        disabled;
                        """,
                        [
                            account.username,
                            account.full_name,
                            account.phone_number,
                            hashed_pw,
                            account.disabled,
                        ],
                    )
                    acc = result.fetchone()
                    return AccountOut(
                        id=acc[0],
                        username=acc[1],
                        full_name=acc[2],
                        phone_number=acc[3],
                        disabled=acc[4],
                    )


        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e),
            )

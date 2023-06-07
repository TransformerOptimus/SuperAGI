from sqlalchemy import Column, Integer, String
from superagi.models.base_model import DBBaseModel


class Organisation(DBBaseModel):
    __tablename__ = 'organisations'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    def __repr__(self):
        return f"Organisation(id={self.id}, name='{self.name}')"

    @classmethod
    def find_or_create_organisation(cls, session, user):
        if user.organisation_id is not None:
            organisation = session.query(Organisation).filter(Organisation.id == user.organisation_id).first()
            return organisation

        existing_organisation = session.query(Organisation).filter(
            Organisation.name == "Default Organization - " + str(user.id)).first()

        if existing_organisation is not None:
            user.organisation_id = existing_organisation.id
            session.commit()
            return existing_organisation

        new_organisation = Organisation(
            name="Default Organization - " + str(user.id),
            description="New default organiztaion",
        )

        session.add(new_organisation)
        session.commit()
        session.flush()
        user.organisation_id = new_organisation.id
        session.commit()
        return new_organisation
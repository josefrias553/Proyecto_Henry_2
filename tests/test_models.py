import sys
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parent.parent))

from models import Base, Usuario, Categoria

class TestModels(unittest.TestCase):
    def setUp(self):

        self.engine = create_engine("sqlite:///:memory:")

        Base.metadata.schema = None
        for table in Base.metadata.tables.values():
            table.schema = None
            
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_create_usuario(self):
        user = Usuario(
            nombre="Test",
            apellido="User",
            dni="12345678",
            email="test@example.com",
            contrasena="hashed_pw"
        )
        self.session.add(user)
        self.session.commit()

        retrieved = self.session.query(Usuario).filter_by(email="test@example.com").first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.nombre, "Test")

    def test_create_categoria(self):
        cat = Categoria(nombre="Electronics", descripcion="Gadgets")
        self.session.add(cat)
        self.session.commit()

        retrieved = self.session.query(Categoria).filter_by(nombre="Electronics").first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.descripcion, "Gadgets")

if __name__ == "__main__":
    unittest.main()

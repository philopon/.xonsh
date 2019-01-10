def _pil_to_image(pil):
    from io import BytesIO
    from iterm2_tools.images import display_image_bytes

    b = BytesIO()
    pil.save(b, format='png')
    return display_image_bytes(b.getbuffer())


def pil_wrapper(module=None, **kwargs):
    def _pil_repr_pretty_(self, p, cycle):
        p.color_results = False
        p.text(_pil_to_image(self))

    module.Image._repr_pretty_ = _pil_repr_pretty_


def rdkit_wrapper(module=None, **kwargs):
    from iterm2_tools.images import display_image_bytes
    from rdkit.Chem.Draw import rdMolDraw2D
    from rdkit.Chem.rdDepictor import SetPreferCoordGen, Compute2DCoords
    from functools import wraps

    SetPreferCoordGen(True)

    GetSubstructMatch = module.Mol.GetSubstructMatch
    GetSubstructMatches = module.Mol.GetSubstructMatches

    @wraps(GetSubstructMatch)
    def _GetSubstructMatch(self, *args, **kwargs):
        res = GetSubstructMatch(self, *args, **kwargs)
        self.__sssAtoms = list(res)
        return res

    @wraps(GetSubstructMatches)
    def _GetSubstructMatches(self, *args, **kwargs):
        res = GetSubstructMatches(self, *args, **kwargs)
        self.__sssAtoms = [a for v in res for a in v]
        return res

    module.Mol.GetSubstructMatch = _GetSubstructMatch
    module.Mol.GetSubstructMatches = _GetSubstructMatches

    def _mol_repr_pretty_(self, p, cycle):
        p.color_results = False
        drawer = rdMolDraw2D.MolDraw2DCairo(300, 300)
        if self.GetNumConformers() == 0:
            Compute2DCoords(self)

        drawer.DrawMolecule(self, highlightAtoms=getattr(self, "__sssAtoms", None))
        drawer.FinishDrawing()
        p.text(display_image_bytes(drawer.GetDrawingText()))

    module.Mol._repr_pretty_ = _mol_repr_pretty_


def handler(module=None, **kwargs):
    if module.__name__ == 'PIL.Image':
        pil_wrapper(module)

    if module.__name__ == 'rdkit.Chem':
        rdkit_wrapper(module)

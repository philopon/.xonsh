def _pil_to_image(pil):
    from io import BytesIO
    from iterm2_tools.images import display_image_bytes

    b = BytesIO()
    pil.save(b, format='png')
    return display_image_bytes(b.getbuffer())


def pil_wrapper(module=None, **kwargs):
    def _pil_repr_pretty_(self, p, cycle):
        p.text(_pil_to_image(self))

    module.Image._repr_pretty_ = _pil_repr_pretty_


def rdkit_wrapper(module=None, **kwargs):
    from rdkit.Chem import Draw

    def _mol_repr_pretty_(self, p, cycle):
        p.text(_pil_to_image(Draw.MolToImage(self)))

    module.Mol._repr_pretty_ = _mol_repr_pretty_


def handler(module=None, **kwargs):
    if module.__name__ == 'PIL.Image':
        pil_wrapper(module)

    if module.__name__ == 'rdkit.Chem':
        rdkit_wrapper(module)

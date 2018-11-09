def rdkit_wrapper(module=None, **kwargs):
    if module.__name__ == 'rdkit.Chem':
        from rdkit.Chem import Draw
        from io import BytesIO
        from iterm2_tools.images import display_image_bytes

        def _mol_repr_pretty_(self, p, cycle):
            b = BytesIO()
            img = Draw.MolToImage(self)
            img.save(b, format='png')
            p.text(display_image_bytes(b.getbuffer()))

        module.Mol._repr_pretty_ = _mol_repr_pretty_

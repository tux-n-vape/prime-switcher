class GPU:
    """
    Class to represent GPU installed on the system

    Attributes
    ----------
    __pci_id : str
        PCI id of the GPU
    __screen : bool
        if GPU manages screen
    __brand : str
        brand of the GPU

    """
    def __init__(self, pci_id: str, screen: bool, brand: str) -> None:
        """
        :param pci_id: PCI id of the GPU
        :param screen: if GPU manages screen
        :param brand: brand of the GPU
        """
        self.__pci_id = pci_id
        self.__screen = screen
        self.__brand = brand

    def get_pci_id(self) -> str:
        """Get PCI id of the GPU"""
        return self.__pci_id

    def has_screen(self) -> bool:
        """Get if GPU manages screen"""
        return self.__screen

    def get_brand(self) -> str:
        """Get brand of the GPU"""
        return self.__brand

    def __repr__(self) -> str:
        return 'pci_id:{},has_screen:{},brand:{}'.format(self.__pci_id, self.__screen, self.__brand)

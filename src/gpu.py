class GPU:
    def __init__(self, pci_id: str, screen: bool, brand: str) -> None:
        self.__pci_id__ = pci_id
        self.__screen__ = screen
        self.__brand__ = brand

    def get_pci_id(self) -> str:
        return self.__pci_id__

    def has_screen(self) -> bool:
        return self.__screen__

    def get_brand(self) -> str:
        return self.__brand__

    def __repr__(self) -> str:
        return 'pci_id:{},has_screen:{},brand:{}'.format(self.__pci_id__, self.__screen__, self.__brand__)

const convertSelectorObjToArray = (obj: object) => {
  return Object.entries(obj).map(([key, value]) => ({
    label: key,
    value: value
  }));
}

export default convertSelectorObjToArray
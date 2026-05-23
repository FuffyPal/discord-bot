def convert_text(text: str) -> str:
    result = []
    
    for char in text:
        if char == 'R':
            result.append('W')
        elif char == 'r':
            result.append('w')
        elif char in ('S', 'Ş'):
            result.append('Sch')
        elif char in ('s', 'ş'):
            result.append('sch')
        elif char == 'Z':
            result.append('Tz')
        elif char == 'z':
            result.append('tz')
        elif char == 'K':
            result.append('Q')
        elif char == 'k':
            result.append('q')
        elif char == 'G':
            result.append('C')
        elif char == 'g':
            result.append('c')
        elif char == 'L':
            result.append('Ly')
        elif char == 'l':
            result.append('ly')
        else:
            result.append(char)
            
    return "".join(result)
#include <string_view>
#include <type_traits>

template <typename T>
constexpr std::string_view get_numpy_format_name()
{
  if constexpr (std::is_floating_point_v<T>)
  {
    if constexpr (sizeof(T) == 4)
      return "=f4";
    else if constexpr (sizeof(T) == 8)
      return "=f8";
    // Handle other floating-point sizes if needed
  }
  else if constexpr (std::is_integral_v<T>)
  {
    if constexpr (std::is_signed_v<T>)
    {
      if constexpr (sizeof(T) == 1)
        return "=i1";
      else if constexpr (sizeof(T) == 2)
        return "=i2";
      else if constexpr (sizeof(T) == 4)
        return "=i4";
      else if constexpr (sizeof(T) == 8)
        return "=i8";
      // Handle other signed integer sizes if needed
    }
    else
    {
      if constexpr (sizeof(T) == 1)
        return "=u1";
      else if constexpr (sizeof(T) == 2)
        return "=u2";
      else if constexpr (sizeof(T) == 4)
        return "=u4";
      else if constexpr (sizeof(T) == 8)
        return "=u8";
      // Handle other unsigned integer sizes if needed
    }
  }
  else if constexpr (std::is_same_v<T, bool>)
  {
    return "=?";
  }
  else
  {
    // this always fails - false cannot be used since the condition must depend on the parameter
    static_assert(!sizeof(T), "Type not supported!");
  }

  return "";
}

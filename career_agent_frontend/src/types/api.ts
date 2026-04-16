export interface UserRegisterRequest {
  username: string;
  email: string;
  password: string;
  role?: string | null;
  studentId?: number | null;
}